import feedparser
import smtplib
import json
import os
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from groq import Groq

# ─── CONFIG ───────────────────────────────────────────────────────────────────

RSS_FEEDS = [
   "https://www.trendingtopics.eu/feed/",
    "https://techcrunch.com/feed/",
    "https://t3n.de/rss.xml",
    "https://retail.at/feed/",
    "https://futurezone.at/xml/rss", 
    # Add as many as you like
]

YOUR_INTERESTS = """
The digest must be written entirely in German, regardless of the original language of the articles.
This includes all summaries and article titles. Translate everything into German.

I'm interested in:
- AI and technology, especially LLMs, AI agents, inference hardware (GPUs, LPUs), and developer tools
- European and Central European politics (Austria, Hungary, EU institutions)
- Investing, fintech, and SaaS (stocks, prediction markets, real estate investment tools)
- Business strategy, product management, and no-code/low-code tools

I am NOT interested in:
- Sports, celebrity gossip, entertainment news
- Generic lifestyle or health content
- US domestic politics unless it has strong EU or global market implications
"""

# ─── ENVIRONMENT VARIABLES ────────────────────────────────────────────────────

EMAIL_FROM     = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_TO"]
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]


# ─── FETCH FEEDS ──────────────────────────────────────────────────────────────

def fetch_recent_items(feeds, hours=72):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items = []

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url)

            for entry in feed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except Exception:
                        pass

                if published is None or published >= cutoff:
                    items.append({
                        "title":     entry.get("title", "No title"),
                        "link":      entry.get("link", ""),
                        "summary":   entry.get("summary", "")[:600],
                        "published": published.isoformat() if published else "unknown",
                        "source":    source_name,
                    })

        except Exception as e:
            print(f"Warning: failed to parse feed {url}: {e}")

    print(f"Fetched {len(items)} total items from {len(feeds)} feeds.")
    return items


# ─── ANALYZE WITH GROQ ────────────────────────────────────────────────────────

def analyze_items(items, interests, batch_size=15):
    if not items:
        return []

    client = Groq(api_key=GROQ_API_KEY)
    all_results = []

    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
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
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,
            )

            raw = response.choices[0].message.content.strip()

            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:].strip()

            batch_results = json.loads(raw)
            all_results.extend(batch_results)

        except json.JSONDecodeError as e:
            print(f"Warning: malformed JSON in batch {idx + 1}: {e}")
        except Exception as e:
            print(f"Warning: batch {idx + 1} failed: {e}")

    return all_results


# ─── DEDUPLICATE ──────────────────────────────────────────────────────────────

def deduplicate_items(items):
    if not items:
        return []

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""You are a news editor. The list below contains news items that may include duplicates — different sources reporting on the same story.

Your task:
1. Identify items that cover the same story or event.
2. Merge them into a single item, keeping the best summary (in German).
3. Collect ALL links from the merged items into a "links" array, each with a "source" and "url" field.
4. For non-duplicate items, still wrap the single link in the same "links" array format.
5. Keep the highest score among merged items.

Return ONLY a valid JSON array. No preamble, no markdown fences.

[
  {{
    "title": "Article title in German",
    "score": 8,
    "summary": "Merged or original summary in German.",
    "links": [
      {{"source": "Feed Source Name", "url": "https://..."}},
      {{"source": "Another Source", "url": "https://..."}}
    ]
  }}
]

Items to deduplicate:
{json.dumps(items, ensure_ascii=False, indent=2)}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith("json"):
                raw = raw[4:].strip()

        deduped = json.loads(raw)
        print(f"      {len(items)} items -> {len(deduped)} after deduplication.")
        return deduped

    except json.JSONDecodeError as e:
        print(f"Warning: deduplication returned malformed JSON: {e}")
        return items
    except Exception as e:
        print(f"Warning: deduplication failed: {e}")
        return items


# ─── FORMAT HTML EMAIL ────────────────────────────────────────────────────────

def format_html_email(analyzed_items):
    DAYS_DE   = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    MONTHS_DE = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    now   = datetime.now()
    today = f"{DAYS_DE[now.weekday()]}, {now.day}. {MONTHS_DE[now.month - 1]} {now.year}"

    num_items   = len(analyzed_items)
    num_sources = len(set(
        l.get("source", "")
        for item in analyzed_items
        for l in item.get("links", [{"source": item.get("source", "")}])
    ))

    if not analyzed_items:
        return f"""
<html><body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 24px; color: #222;">
<h1 style="border-bottom: 2px solid #222; padding-bottom: 8px;">Daily Digest</h1>
<p style="color: #666;">{today}</p>
<p>Heute keine relevanten Artikel gefunden. Genieß die Stille.</p>
</body></html>
"""

    sorted_items = sorted(analyzed_items, key=lambda x: x.get("score", 0), reverse=True)

    def score_color(s):
        if s >= 7: return "#2a7a2a"
        if s >= 4: return "#b05c00"
        return "#888888"

    html = f"""
<html>
<body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 24px 16px; color: #1a1a1a; background: #fff;">

<h1 style="font-size: 26px; border-bottom: 2px solid #1a1a1a; padding-bottom: 10px; margin-bottom: 4px;">
  Daily Digest
</h1>
<p style="color: #888; font-size: 13px; margin-top: 4px;">
  {today} &nbsp;|&nbsp; {num_items} Artikel aus {num_sources} Quelle{"n" if num_sources != 1 else ""}
</p>
"""

    for item in sorted_items:
        score   = item.get("score", 0)
        title   = item.get("title", "Kein Titel")
        summary = item.get("summary", "")
        links   = item.get("links", [{"source": item.get("source", "Quelle"), "url": item.get("link", "#")}])
        color   = score_color(score)

        link_html = " &nbsp; ".join(
            f'<a href="{l.get("url","#")}" style="font-size: 12px; color: #555; text-decoration: none;">'
            f'{l.get("source","Quelle")} &rarr;</a>'
            for l in links
        )

        html += f"""
<div style="margin-bottom: 18px; padding: 14px 16px; background: #f7f7f7;
            border-radius: 6px; border: 1px solid #e8e8e8;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="vertical-align: top;">
      <span style="font-size: 15px; font-weight: bold; color: #1a1a1a; line-height: 1.4;">{title}</span>
    </td>
    <td style="vertical-align: top; text-align: right; white-space: nowrap; padding-left: 12px;">
      <span style="color: {color}; font-weight: bold; font-size: 13px;">{score}/10</span>
    </td>
  </tr></table>
  <p style="margin: 8px 0 10px 0; font-size: 14px; line-height: 1.55; color: #333;">{summary}</p>
  <div>{link_html}</div>
</div>
"""

    html += """
<hr style="border: none; border-top: 1px solid #ddd; margin-top: 40px;">
<p style="font-size: 11px; color: #bbb; text-align: center;">
  Automatisch erstellt mit Groq &amp; GitHub Actions.
</p>
</body></html>
"""
    return html


# ─── SEND EMAIL ───────────────────────────────────────────────────────────────

def send_email(html_body, from_addr, to_addr, password):
    today = datetime.now().strftime("%d.%m.%Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Digest — {today}"
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())

    print(f"E-Mail gesendet an {to_addr}.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Daily Digest ===")

    print("\n[1/4] RSS-Feeds abrufen...")
    items = fetch_recent_items(RSS_FEEDS, hours=24)

    if not items:
        print("Keine Artikel gefunden. Leere Zusammenfassung wird gesendet.")
        html = format_html_email([])
        send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)
    else:
        print(f"\n[2/4] {len(items)} Artikel zur Analyse an Groq senden...")
        analyzed = analyze_items(items, YOUR_INTERESTS)
        analyzed = [i for i in analyzed if i.get("score", 0) >= 5]
        print(f"      {len(analyzed)} relevante Artikel nach dem Filtern.")

        print("\n[2b/4] Duplikate entfernen...")
        analyzed = deduplicate_items(analyzed)

        print("\n[3/4] HTML-E-Mail formatieren...")
        html = format_html_email(analyzed)

        print("\n[4/4] E-Mail senden...")
        send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)

    print("\nFertig.")
