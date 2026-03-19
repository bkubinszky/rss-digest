import json
import urllib.request
from groq import Groq, APIStatusError
from config import GROQ_API_KEY, GEMINI_API_KEY


# ─── LLM CALL WITH FALLBACK ───────────────────────────────────────────────────

def call_llm(prompt, label=""):
    """Try Groq first. If rate-limited or failed, fall back to Gemini."""

    # — Groq —
    try:
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
        )
        return response.choices[0].message.content.strip(), "Groq"

    except APIStatusError as e:
        if e.status_code == 429:
            print(f"      Groq rate limit hit{' (' + label + ')' if label else ''}. Falling back to Gemini...")
        else:
            print(f"      Groq error ({e.status_code}){' (' + label + ')' if label else ''}. Falling back to Gemini...")

    except Exception as e:
        print(f"      Groq unexpected error: {e}. Falling back to Gemini...")

    # — Gemini fallback —
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4000}
        }).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        return text, "Gemini"

    except Exception as e:
        raise RuntimeError(f"Both Groq and Gemini failed: {e}")


def clean_json(raw):
    """Strip markdown fences from LLM JSON responses."""
    if raw.startswith("```"):
        parts = raw.split("```")
        raw = parts[1] if len(parts) > 1 else raw
        if raw.startswith("json"):
            raw = raw[4:].strip()
    return raw


# ─── ANALYZE ──────────────────────────────────────────────────────────────────

def analyze_items(items, interests, batch_size=15):
    """Filter, score, summarize and translate items in batches."""
    if not items:
        return [], []

    all_results = []
    api_errors  = []
    api_usage   = {"Groq": 0, "Gemini": 0}
    batches     = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    print(f"      Processing {len(items)} items in {len(batches)} batches of up to {batch_size}...")

    for idx, batch in enumerate(batches):
        print(f"      Batch {idx + 1}/{len(batches)}...")

        prompt = f"""You are a precise and opinionated news curator. Analyze the RSS feed items below and produce a structured daily digest.

## My interests and filters:
{interests}

## Your tasks:
1. **Filter**: Discard any item that is not clearly relevant to my interests. Be strict.
2. **Score**: Assign each remaining item a relevance score from 1 to 10.
3. **Summarize**: Write a concise 1-2 sentence summary in German. Do not copy the original text.
4. **Translate**: Translate the article title into German.
5. **Link**: Preserve the original URL.

## Output format:
Return ONLY a valid JSON array. No preamble, no explanation, no markdown code fences.

[
  {{
    "title": "Article title translated into German",
    "source": "Feed source name",
    "link": "https://...",
    "score": 8,
    "summary": "1-2 sentence summary in German."
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

        except RuntimeError as e:
            error_msg = f"Batch {idx + 1}/{len(batches)}: {e}"
            print(f"      ERROR: {error_msg}")
            api_errors.append(error_msg)

        except json.JSONDecodeError as e:
            print(f"      Warning: malformed JSON in batch {idx + 1}: {e}")

    return all_results, api_errors, api_usage
