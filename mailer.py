import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import MOCK_MODE, SOURCE_SCORE_THRESHOLD, SOURCE_MAX_ARTICLES


def _build_source_sections(analyzed_items):
    """Group items by source, apply display rules, return ordered list of source blocks.

    Per source:
    - Show all articles scoring SOURCE_SCORE_THRESHOLD or above
    - If fewer than SOURCE_MAX_ARTICLES score that high, fill up to SOURCE_MAX_ARTICLES
      with the next highest scoring articles
    - Sort articles within each source by score descending
    - Top article gets summary + why_it_matters; rest get title + link only
    - Sources ordered by their top article's score descending
    """
    # Group by source
    sources = {}
    for item in analyzed_items:
        # Items may come from deduplicator with a "links" array,
        # or directly from analyzer with a single "source" field
        links  = item.get("links", [{"source": item.get("source", "Unbekannt"), "url": item.get("link", "#")}])
        source = links[0].get("source", "Unbekannt")
        sources.setdefault(source, []).append(item)

    # Apply display rules per source
    source_blocks = []
    for source, items in sources.items():
        sorted_items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)

        above_threshold = [i for i in sorted_items if i.get("score", 0) >= SOURCE_SCORE_THRESHOLD]

        if len(above_threshold) >= SOURCE_MAX_ARTICLES:
            display_items = above_threshold
        else:
            display_items = sorted_items[:SOURCE_MAX_ARTICLES]

        top_score = display_items[0].get("score", 0) if display_items else 0
        source_blocks.append((source, display_items, top_score))

    # Order sources by top article score descending
    source_blocks.sort(key=lambda x: x[2], reverse=True)
    return source_blocks


def format_html_email(analyzed_items, feed_warnings=None):
    """Build a clean HTML email grouped by source."""
    DAYS_DE   = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    MONTHS_DE = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    now   = datetime.now()
    today = f"{DAYS_DE[now.weekday()]}, {now.day}. {MONTHS_DE[now.month - 1]} {now.year}"

    num_items   = len(analyzed_items)
    num_sources = len(set(
        item.get("links", [{"source": item.get("source", "")}])[0].get("source", "")
        for item in analyzed_items
    ))

    # ── Banners ───────────────────────────────────────────────────────────────

    mock_banner = ""
    if MOCK_MODE:
        mock_banner = """
<div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 6px;
            padding: 10px 14px; margin: 12px 0; font-size: 13px; color: #856404;">
  &#9888;&#65039; MOCK MODE — Diese Ausgabe enthält Testdaten. Kein echter Inhalt.
</div>
"""

    feed_warning_banner = ""
    if feed_warnings:
        feed_list = "".join(
            f"<li style='margin-bottom: 4px;'>"
            f"<strong>{w['source']}</strong> — {w['consecutive_failures']} Tage in Folge fehlgeschlagen"
            f"</li>"
            for w in feed_warnings
        )
        feed_warning_banner = f"""
<div style="background: #fdecea; border: 1px solid #f44336; border-radius: 6px;
            padding: 10px 14px; margin: 12px 0; font-size: 13px; color: #c62828;">
  &#9888;&#65039; <strong>Feed-Warnung:</strong> Die folgenden Quellen konnten seit mehreren Tagen nicht abgerufen werden:
  <ul style="margin: 6px 0 0 0; padding-left: 18px;">
    {feed_list}
  </ul>
  Bitte die Feed-URLs in <code>config.py</code> prüfen.
</div>
"""

    if not analyzed_items:
        return f"""
<html><body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 24px; color: #222;">
<h1 style="border-bottom: 2px solid #222; padding-bottom: 8px;">Daily Digest</h1>
<p style="color: #666;">{today}</p>
{mock_banner}
{feed_warning_banner}
<p>Heute keine relevanten Artikel gefunden. Genieß die Stille.</p>
</body></html>
"""

    source_blocks = _build_source_sections(analyzed_items)

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
{mock_banner}
{feed_warning_banner}
"""

    for source, items, _ in source_blocks:
        html += f"""
<div style="margin-top: 32px;">
  <h2 style="font-size: 17px; color: #1a1a1a; margin-bottom: 10px;
             border-left: 4px solid #888; padding-left: 12px;">
    {source}
  </h2>
"""
        for i, item in enumerate(items):
            score         = item.get("score", 0)
            title         = item.get("title", "No title")
            summary       = item.get("summary", "")
            why           = item.get("why_it_matters", "")
            links         = item.get("links", [{"source": source, "url": item.get("link", "#")}])
            color         = score_color(score)
            is_top        = (i == 0)

            link_html = " &nbsp; ".join(
                f'<a href="{l.get("url","#")}" style="font-size: 12px; color: #555; text-decoration: none;">'
                f'{l.get("source", source)} &rarr;</a>'
                for l in links
            )

            if is_top:
                # Top article: title, score, summary, why it matters, links
                html += f"""
<div style="margin-bottom: 14px; padding: 14px 16px; background: #f7f7f7;
            border-radius: 6px; border: 1px solid #e8e8e8;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="vertical-align: top;">
      <span style="font-size: 15px; font-weight: bold; color: #1a1a1a; line-height: 1.4;">{title}</span>
    </td>
    <td style="vertical-align: top; text-align: right; white-space: nowrap; padding-left: 12px;">
      <span style="color: {color}; font-weight: bold; font-size: 13px;">{score}/10</span>
    </td>
  </tr></table>
  <p style="margin: 8px 0 4px 0; font-size: 14px; line-height: 1.55; color: #333;">{summary}</p>
  <p style="margin: 0 0 10px 0; font-size: 13px; line-height: 1.5; color: #555;
            font-style: italic; border-left: 3px solid #ccc; padding-left: 8px;">
    {why}
  </p>
  <div>{link_html}</div>
</div>
"""
            else:
                # Other articles: title, score, link only
                primary_url = links[0].get("url", "#") if links else "#"
                html += f"""
<div style="margin-bottom: 6px; padding: 8px 12px; font-size: 14px; color: #1a1a1a;
            border-left: 2px solid #ddd;">
  <table width="100%" cellpadding="0" cellspacing="0"><tr>
    <td style="vertical-align: middle;">
      <a href="{primary_url}" style="color: #1a1a8c; text-decoration: none; font-size: 14px;">{title}</a>
    </td>
    <td style="vertical-align: middle; text-align: right; white-space: nowrap; padding-left: 12px;">
      <span style="color: {color}; font-weight: bold; font-size: 12px;">{score}/10</span>
    </td>
  </tr></table>
</div>
"""

        html += "</div>"  # close source block

    html += """
<hr style="border: none; border-top: 1px solid #ddd; margin-top: 40px;">
<p style="font-size: 11px; color: #bbb; text-align: center;">
  Automatisch erstellt mit Gemini &amp; GitHub Actions.
</p>
</body></html>
"""
    return html


def format_error_email(errors):
    """Build an error notification email listing what went wrong."""
    today      = datetime.now().strftime("%d.%m.%Y %H:%M")
    error_list = "".join(f"<li style='margin-bottom:8px;'>{e}</li>" for e in errors)

    return f"""
<html>
<body style="font-family: Georgia, serif; max-width: 680px; margin: 0 auto; padding: 24px 16px; color: #1a1a1a;">
<h1 style="font-size: 22px; color: #c00; border-bottom: 2px solid #c00; padding-bottom: 10px;">
  Daily Digest — Fehler aufgetreten
</h1>
<p style="color: #888; font-size: 13px;">{today}</p>
<p>Der heutige Digest konnte nicht vollständig erstellt werden, weil beide APIs (Gemini und Groq) fehlgeschlagen sind.</p>
<p><strong>Fehlermeldungen:</strong></p>
<ul style="font-size: 14px; line-height: 1.6; color: #333;">
  {error_list}
</ul>
<p style="margin-top: 24px; font-size: 13px; color: #666;">
  Mögliche Ursachen: tägliches Token-Limit bei Gemini und/oder Groq erreicht, oder API-Key ungültig.
  Bitte <a href="https://aistudio.google.com">aistudio.google.com</a> und
  <a href="https://console.groq.com">console.groq.com</a> prüfen.
</p>
</body></html>
"""


def send_email(html_body, from_addr, to_addr, password, subject):
    """Send the digest via Gmail SMTP using SSL."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_addr
    msg["To"]      = to_addr
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(from_addr, password)
        server.sendmail(from_addr, to_addr, msg.as_string())

    print(f"E-Mail gesendet an {to_addr}.")
