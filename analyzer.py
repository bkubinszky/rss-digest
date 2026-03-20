import json
import time
import urllib.request
import urllib.error
from groq import Groq, APIStatusError
from config import GROQ_API_KEY, GEMINI_API_KEY, GROQ_MODEL, GEMINI_MODEL, BATCH_SIZE, MAX_RETRIES, BACKOFF_BASE


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def clean_json(raw):
    """Strip markdown fences from LLM JSON responses."""
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:].strip()
    return raw


def is_transient(e):
    """Return True if the error is likely temporary and worth retrying."""
    transient_types = (TimeoutError, ConnectionError, urllib.error.URLError)
    if isinstance(e, transient_types):
        return True
    if isinstance(e, urllib.error.HTTPError) and e.code >= 500:
        return True
    return False


# ─── LLM CALL WITH FALLBACK AND RETRY ────────────────────────────────────────

def call_llm(prompt, label=""):
    """Try Gemini first with retry/backoff, then fall back to Groq with retry/backoff."""

    # — Gemini (primary) —
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
            payload = json.dumps({
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4000}
            }).encode("utf-8")

            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            return text, "Gemini"

        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = BACKOFF_BASE * (2 ** (attempt - 1))
                print(f"      Gemini rate limit/server error ({e.code}), attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"      Gemini non-retriable error (HTTP {e.code}){' (' + label + ')' if label else ''}. Falling back to Groq...")
                break

        except Exception as e:
            if is_transient(e):
                wait = BACKOFF_BASE * (2 ** (attempt - 1))
                print(f"      Gemini transient error ({e}), attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                print(f"      Gemini unexpected error: {e}. Falling back to Groq...")
                break

    # — Groq (fallback) —
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,
            )
            return response.choices[0].message.content.strip(), "Groq"

        except APIStatusError as e:
            if e.status_code == 429:
                wait = BACKOFF_BASE * (2 ** (attempt - 1))
                print(f"      Groq rate limit hit, attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
                time.sleep(wait)
            elif e.status_code >= 500:
                wait = BACKOFF_BASE * (2 ** (attempt - 1))
                print(f"      Groq server error ({e.status_code}), attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Groq non-retriable error: HTTP {e.status_code}")

        except Exception as e:
            if is_transient(e):
                wait = BACKOFF_BASE * (2 ** (attempt - 1))
                print(f"      Groq transient error ({e}), attempt {attempt}/{MAX_RETRIES}. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Groq unexpected error: {e}")

    raise RuntimeError(f"Both Gemini and Groq failed after {MAX_RETRIES} attempts each.")


# ─── ANALYZE ──────────────────────────────────────────────────────────────────

def analyze_items(items, interests):
    """Filter, score, summarize and annotate items in batches."""
    from config import MOCK_MODE
    from mock import MOCK_ANALYZED_ITEMS
    if MOCK_MODE:
        print("      MOCK MODE: skipping LLM calls, returning mock data.")
        return MOCK_ANALYZED_ITEMS, [], {"Groq": 0, "Gemini": 0}

    if not items:
        return [], [], {}

    all_results = []
    api_errors  = []
    api_usage   = {"Groq": 0, "Gemini": 0}
    batches     = [items[i:i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
    print(f"      Processing {len(items)} items in {len(batches)} batches of up to {BATCH_SIZE}...")

    for idx, batch in enumerate(batches):
        print(f"      Batch {idx + 1}/{len(batches)}...")

        prompt = f"""You are a precise and opinionated news curator. Analyze the RSS feed items below and produce a structured daily digest.

## My interests and filters:
{interests}

## Your tasks:
1. **Filter**: Discard any item that is not clearly relevant to my interests. Be strict.
2. **Score**: Assign each remaining item a relevance score from 1 to 10.
3. **Keep original title**: Do NOT translate the title. Keep it exactly as it appears in the source.
4. **Summarize**: Write a concise 2-sentence summary in German.
5. **Why it matters**: Write 1 sentence in German explaining why this article is actionable or relevant from a monetization perspective.
6. **Link**: Preserve the original URL.

## Output format:
Return ONLY a valid JSON array. No preamble, no explanation, no markdown code fences.

[
  {{
    "title": "Original article title, unchanged",
    "source": "Feed source name",
    "link": "https://...",
    "score": 8,
    "summary": "2-sentence summary in German.",
    "why_it_matters": "1 sentence in German on monetization relevance."
  }}
]

## Items to analyze:
{json.dumps(batch, ensure_ascii=False, indent=2)}
"""

        try:
            raw, api_used = call_llm(prompt, label=f"batch {idx + 1}")
            api_usage[api_used] = api_usage.get(api_used, 0) + 1
            print(f"      (answered by {api_used})")
            batch_results = json.loads(clean_json(raw))
            all_results.extend(batch_results)
            if api_used == "Groq":
                time.sleep(5)

        except RuntimeError as e:
            error_msg = f"Batch {idx + 1}/{len(batches)}: {e}"
            print(f"      ERROR: {error_msg}")
            api_errors.append(error_msg)

        except json.JSONDecodeError as e:
            print(f"      Warning: malformed JSON in batch {idx + 1}: {e}")

    return all_results, api_errors, api_usage
