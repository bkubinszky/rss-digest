import feedparser
import smtplib
import json
import os
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from groq import Groq

# ─── CONFIG ───────────────────────────────────────────────────────────────────
# Add or remove feeds here

RSS_FEEDS = [
    "https://www.trendingtopics.eu/feed/",
    "https://techcrunch.com/feed/",
    "https://t3n.de/rss.xml",
    "https://retail.at/feed/",
    "https://futurezone.at/xml/rss", 
    # Add as many as you like
]

# This is your main lever. Be specific — the more precise you are,
# the better the filtering and scoring will be.
YOUR_INTERESTS = """
The digest must be written entirely in German, regardless of the original language of the articles. This includes all summaries, topic group names, and any other text you generate. Translate and summarize into German.
I'm interested in:
- AI and technology, especially LLMs, AI agents, agentic commerce, developer tools
- European and Central European politics (Austria, Hungary, EU institutions)
- Investing, fintech, and SaaS (stocks, prediction markets, real estate investment tools, crypto)
- For investing, focus on European and global markets, US-domestic markets only if strong implications for the rest of the world
- Business strategy, product management, and no-code/low-code tools
- Business ideas and news relevant to early-stage SaaS or solo founders
- Keep summaries concise and neutral, no hype

I am NOT interested in:
- Sports, celebrity gossip, entertainment news
- Generic lifestyle or health content
- US domestic politics unless it has strong EU or global market implications
"""

# ─── ENVIRONMENT VARIABLES (set these as GitHub Secrets) ──────────────────────
EMAIL_FROM     = os.environ["EMAIL_FROM"]       # your Gmail address
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]   # your Gmail App Password (not your real password)
EMAIL_TO       = os.environ["EMAIL_TO"]         # where to send the digest (can be same as FROM)
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]


# ─── FETCH FEEDS ──────────────────────────────────────────────────────────────

def fetch_recent_items(feeds, hours=24):
    """Fetch all feed entries published within the last N hours."""
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

                # Include if within cutoff, or if no date info is available
                if published is None or published >= cutoff:
                    items.append({
                        "title":     entry.get("title", "No title"),
                        "link":      entry.get("link", ""),
                        "summary":   entry.get("summary", "")[:600],  # truncate to save tokens
                        "published": published.isoformat() if published else "unknown",
                        "source":    source_name,
                    })

        except Exception as e:
            print(f"Warning: failed to parse feed {url}: {e}")

    print(f"Fetched {len(items)} total items from {len(feeds)} feeds.")
    return items


# ─── ANALYZE WITH GROQ ────────────────────────────────────────────────────────

def analyze_items(items, interests, batch_size=15):
    """Send items to Groq in batches to stay within token limits."""
    if not items:
        return []
 
    client = Groq(api_key=GROQ_API_KEY)
    all_results = []
 
    # Split items into chunks of batch_size
    batches = [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    print(f"      Processing {len(items)} items in {len(batches)} batches of up to {batch_size}...")
 
    for idx, batch in enumerate(batches):
        print(f"      Batch {idx + 1}/{len(batches)}...")
 
        prompt = f"""You are a precise and opinionated news curator. Analyze the RSS feed items below and produce a structured daily digest.
 
## My interests and filters:
{interests}
 
## Your tasks:
1. **Filter**: Discard any item that is not clearly relevant to my interests. Be strict — tangential or generic items should be excluded.
2. **Score**: Assign each remaining item a relevance score from 1 to 10 (10 = extremely relevant and interesting to me).
3. **Group**: Assign each item to a descriptive topic group. Invent sensible groups based on what's present (e.g. "AI & Developer Tools", "European Politics", "Investing & Markets"). Use 2-6 groups max.
4. **Summarize**: Write a concise 1-2 sentence summary of each item in plain English. Do not copy the original text — paraphrase and add context if helpful.
5. **Link**: Preserve the original URL.
 
## Output format:
Return ONLY a valid JSON array. No preamble, no explanation, no markdown code fences.
 
[
  {{
    "title": "Original article title",
    "source": "Feed source name",
    "link": "https://...",
    "topic": "Topic Group Name",
    "score": 8,
    "summary": "Your 1-2 sentence summary here."
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
 
            # Strip markdown fences if the model adds them anyway
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
    

# ─── FORMAT HTML EMAIL ────────────────────────────────────────────────────────

def format_html_email(analyzed_items):
    """Build a clean HTML email from the analyzed and grouped items."""
    today = datetime.now().strftime("%A, %B %d, %Y")
    num_items = len(analyzed_items)
    num_sources = len(set(i.get("source", "") for i in analyzed_items))

    if not analyzed_items:
        return f"""
<html><body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 24px; color: #222;">
<h1 style="border-bottom: 2px solid #222; padding-bottom: 8px;">Daily Digest</h1>
<p style="color: #666;">{today}</p>
<p>Nothing relevant found in the last 24 hours. Enjoy the silence.</p>
</body></html>
"""

    # Group by topic, sort by score descending within each group
    topics = {}
    for item in analyzed_items:
        topic = item.get("topic", "General")
        topics.setdefault(topic, []).append(item)
    for topic in topics:
        topics[topic].sort(key=lambda x: x.get("score", 0), reverse=True)

    html = f"""
<html>
<body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 24px 16px; color: #1a1a1a; background: #fff;">

<h1 style="font-size: 26px; border-bottom: 2px solid #1a1a1a; padding-bottom: 10px; margin-bottom: 4px;">
  Daily Digest
</h1>
<p style="color: #888; font-size: 13px; margin-top: 4px;">
  {today} &nbsp;|&nbsp; {num_items} item{"s" if num_items != 1 else ""} from {num_sources} source{"s" if num_sources != 1 else ""}
</p>
"""

    score_color_map = lambda s: "#2a7a2a" if s >= 7 else "#b05c00" if s >= 4 else "#888888"

    for topic in sorted(topics.keys()):
        items = topics[topic]
        html += f"""
<h2 style="font-size: 18px; color: #1a1a1a; margin-top: 36px; margin-bottom: 12px;
           border-left: 4px solid #444; padding-left: 12px;">
  {topic}
</h2>
"""
        for item in items:
            score = item.get("score", 0)
            color = score_color_map(score)
            title = item.get("title", "Untitled")
            link = item.get("link", "#")
            source = item.get("source", "")
            summary = item.get("summary", "")

            html += f"""
<div style="margin-bottom: 18px; padding: 14px 16px; background: #f7f7f7;
            border-radius: 6px; border: 1px solid #e8e8e8;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="vertical-align: top;">
      <a href="{link}" style="font-size: 15px; font-weight: bold; color: #1a1a8c;
                              text-decoration: none; line-height: 1.4;">{title}</a>
    </td>
    <td style="vertical-align: top; text-align: right; white-space: nowrap; padding-left: 12px;">
      <span style="color: {color}; font-weight: bold; font-size: 13px;">{score}/10</span>
    </td>
  </tr></table>
  <div style="font-size: 11px; color: #999; margin: 4px 0 8px 0;">{source}</div>
  <p style="margin: 0; font-size: 14px; line-height: 1.55; color: #333;">{summary}</p>
  <a href="{link}" style="display: inline-block; margin-top: 10px; font-size: 12px;
                          color: #555; text-decoration: none;">
    Read original &rarr;
  </a>
</div>
"""

    html += """
<hr style="border: none; border-top: 1px solid #ddd; margin-top: 40px;">
<p style="font-size: 11px; color: #bbb; text-align: center;">
  Generated by your RSS digest script. Powered by Groq + GitHub Actions.
</p>
</body></html>
"""
    return html


# ─── SEND EMAIL ───────────────────────────────────────────────────────────────

def send_email(html_body, from_addr, to_addr, password):
    """Send the digest via Gmail SMTP using SSL."""
    today = datetime.now().strftime("%b %d, %Y")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Digest — {today}"
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())

    print(f"Email sent to {to_addr}.")


# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Daily Digest Runner ===")

    print("\n[1/4] Fetching RSS feeds...")
    items = fetch_recent_items(RSS_FEEDS, hours=24)

    if not items:
        print("No items found. Sending empty digest.")
        html = format_html_email([])
        send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)
    else:
        print(f"\n[2/4] Sending {len(items)} items to Groq for analysis...")
        analyzed = analyze_items(items, YOUR_INTERESTS)
        print(f"      {len(analyzed)} relevant items after filtering.")

        print("\n[3/4] Formatting HTML email...")
        html = format_html_email(analyzed)

        print("\n[4/4] Sending email...")
        send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD)

    print("\nDone.")
