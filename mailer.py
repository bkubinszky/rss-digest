import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import MOCK_MODE, SOURCE_SCORE_THRESHOLD, SOURCE_MAX_ARTICLES


def _build_source_sections(analyzed_items):
    """Group items by source, apply display rules, return ordered list of source blocks."""
    sources = {}
    for item in analyzed_items:
        source = item.get("source", "Unbekannt")
        sources.setdefault(source, []).append(item)

    source_blocks = []
    for source, items in sources.items():
        sorted_items    = sorted(items, key=lambda x: x.get("score", 0), reverse=True)
        above_threshold = [i for i in sorted_items if i.get("score", 0) >= SOURCE_SCORE_THRESHOLD]

        if len(above_threshold) >= SOURCE_MAX_ARTICLES:
            display_items = above_threshold
        else:
            display_items = sorted_items[:SOURCE_MAX_ARTICLES]

        top_score = display_items[0].get("score", 0) if display_items else 0
        source_blocks.append((source, display_items, top_score))

    source_blocks.sort(key=lambda x: x[2], reverse=True)
    return source_blocks


def _score_pill(score):
    """Return a small inline score badge styled by score range."""
    if score >= 8:
        bg, color = "#d4edda", "#1a5c2a"
    elif score >= 6:
        bg, color = "#fff3cd", "#856404"
    else:
        bg, color = "#f0f0f0", "#666666"

    return (
        f'<span style="display: inline-block; background: {bg}; color: {color}; '
        f'font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 10px; '
        f'letter-spacing: 0.02em; font-family: Georgia, serif;">{score}</span>'
    )


def format_html_email(analyzed_items, feed_warnings=None):
    """Build a clean editorial HTML email grouped by source."""
    DAYS_DE   = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    MONTHS_DE = ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"]
    now   = datetime.now()
    today = f"{DAYS_DE[now.weekday()]}, {now.day}. {MONTHS_DE[now.month - 1]} {now.year}"

    num_items   = 0  # calculated after source_blocks are built
    num_sources = len(set(item.get("source", "") for item in analyzed_items))

    # ── Banners ───────────────────────────────────────────────────────────────

    mock_banner = ""
    if MOCK_MODE:
        mock_banner = """
<tr><td style="padding: 0 0 16px 0;">
  <div style="background: #fff8e1; border-left: 3px solid #f9a825; padding: 10px 14px;
              font-size: 12px; color: #795548; font-family: Georgia, serif;">
    MOCK MODE &mdash; Testdaten. Kein echter Inhalt.
  </div>
</td></tr>
"""

    feed_warning_banner = ""
    if feed_warnings:
        feed_list = "".join(
            f"<li style='margin-bottom: 3px;'>{w['source']} &mdash; {w['consecutive_failures']} Tage fehlgeschlagen</li>"
            for w in feed_warnings
        )
        feed_warning_banner = f"""
<tr><td style="padding: 0 0 16px 0;">
  <div style="background: #fdecea; border-left: 3px solid #c62828; padding: 10px 14px;
              font-size: 12px; color: #c62828; font-family: Georgia, serif;">
    <strong>Feed-Warnung</strong>
    <ul style="margin: 6px 0 0 0; padding-left: 16px;">{feed_list}</ul>
  </div>
</td></tr>
"""

    if not analyzed_items:
        return f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; background: #ffffff;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff;">
  <tr><td align="center" style="padding: 48px 24px;">
    <table width="600" cellpadding="0" cellspacing="0">
      <tr><td style="padding-bottom: 6px;">
        <table width="100%" cellpadding="0" cellspacing="0"><tr>
          <td style="font-family: Georgia, 'Times New Roman', serif; font-size: 28px;
                     font-style: italic; color: #1a1a1a;">Daily Digest</td>
          <td align="right" style="font-family: Georgia, serif; font-size: 11px;
                                   color: #999; letter-spacing: 0.08em; text-transform: uppercase;
                                   vertical-align: bottom; padding-bottom: 4px;">{today}</td>
        </tr></table>
      </td></tr>
      <tr><td style="border-top: 1px solid #1a1a1a; padding-top: 32px;
                     font-family: Georgia, serif; font-size: 14px; color: #666;">
        Heute keine relevanten Artikel gefunden.
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>
"""

    source_blocks = _build_source_sections(analyzed_items)
    num_items = sum(len(items) for _, items, _ in source_blocks)

    # ── Build source sections ─────────────────────────────────────────────────
    sections_html = ""
    for source, items, _ in source_blocks:
        rows = ""
        for item in items:
            score = item.get("score", 0)
            title = item.get("title", "No title")
            link  = item.get("link", "#")
            pill  = _score_pill(score)

            rows += f"""
<tr>
  <td style="padding: 11px 0; border-bottom: 1px solid #f0f0f0;">
    <table width="100%" cellpadding="0" cellspacing="0"><tr>
      <td style="font-family: Georgia, 'Times New Roman', serif; font-size: 15px;
                 color: #1a1a1a; line-height: 1.4; vertical-align: middle;">
        <a href="{link}" style="color: #1a1a1a; text-decoration: none;">{title}</a>
      </td>
      <td align="right" style="vertical-align: middle; padding-left: 16px; white-space: nowrap;">
        {pill}
      </td>
    </tr></table>
  </td>
</tr>
"""

        sections_html += f"""
<tr><td style="padding-top: 32px; padding-bottom: 8px;">
  <p style="margin: 0 0 8px 0; font-family: Georgia, serif; font-size: 11px;
            letter-spacing: 0.1em; text-transform: uppercase; color: #999;
            font-style: normal;">{source.upper()}</p>
  <table width="100%" cellpadding="0" cellspacing="0" style="border-top: 1px solid #e0e0e0;">
    {rows}
  </table>
</td></tr>
"""

    # ── Full email ────────────────────────────────────────────────────────────
    return f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; background: #ffffff;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff;">
  <tr><td align="center" style="padding: 48px 24px 64px 24px;">
    <table width="600" cellpadding="0" cellspacing="0">

      <!-- Header -->
      <tr><td style="padding-bottom: 6px;">
        <table width="100%" cellpadding="0" cellspacing="0"><tr>
          <td style="font-family: Georgia, 'Times New Roman', serif; font-size: 28px;
                     font-style: italic; color: #1a1a1a; vertical-align: bottom;">
            Daily Digest
          </td>
          <td align="right" style="font-family: Georgia, serif; font-size: 11px;
                                   color: #999; letter-spacing: 0.08em; text-transform: uppercase;
                                   vertical-align: bottom; padding-bottom: 5px;">
            {today}
          </td>
        </tr></table>
      </td></tr>

      <!-- Header rule -->
      <tr><td style="border-top: 1px solid #1a1a1a; padding-bottom: 4px;"></td></tr>

      <!-- Meta -->
      <tr><td style="padding: 10px 0 0 0; font-family: Georgia, serif; font-size: 11px;
                     color: #bbb; letter-spacing: 0.04em;">
        {num_items} Artikel &middot; {num_sources} Quellen
      </td></tr>

      <!-- Banners -->
      {mock_banner}
      {feed_warning_banner}

      <!-- Source sections -->
      {sections_html}

      <!-- Footer -->
      <tr><td style="padding-top: 48px; border-top: 1px solid #e8e8e8;">
        <p style="margin: 0; font-family: Georgia, serif; font-size: 11px;
                  color: #bbb; text-align: center; letter-spacing: 0.04em;">
          Automatisch erstellt mit Gemini &amp; GitHub Actions
        </p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body></html>
"""


def format_error_email(errors):
    """Build a clean error notification email."""
    today      = datetime.now().strftime("%d.%m.%Y %H:%M")
    error_list = "".join(f"<li style='margin-bottom:6px;'>{e}</li>" for e in errors)

    return f"""
<!DOCTYPE html>
<html>
<body style="margin: 0; padding: 0; background: #ffffff;">
<table width="100%" cellpadding="0" cellspacing="0" style="background: #ffffff;">
  <tr><td align="center" style="padding: 48px 24px;">
    <table width="600" cellpadding="0" cellspacing="0">
      <tr><td style="padding-bottom: 6px;">
        <table width="100%" cellpadding="0" cellspacing="0"><tr>
          <td style="font-family: Georgia, serif; font-size: 28px; font-style: italic; color: #c00;">
            Daily Digest
          </td>
          <td align="right" style="font-family: Georgia, serif; font-size: 11px; color: #999;
                                   letter-spacing: 0.08em; text-transform: uppercase;
                                   vertical-align: bottom; padding-bottom: 5px;">{today}</td>
        </tr></table>
      </td></tr>
      <tr><td style="border-top: 1px solid #c00; padding-top: 24px;
                     font-family: Georgia, serif; font-size: 14px; color: #333; line-height: 1.6;">
        <p style="margin: 0 0 16px 0;">
          Der heutige Digest konnte nicht erstellt werden — beide APIs (Gemini und Groq) sind fehlgeschlagen.
        </p>
        <ul style="margin: 0 0 16px 0; padding-left: 18px; font-size: 13px; color: #666;">
          {error_list}
        </ul>
        <p style="margin: 0; font-size: 12px; color: #999;">
          Bitte <a href="https://aistudio.google.com" style="color: #999;">aistudio.google.com</a> und
          <a href="https://console.groq.com" style="color: #999;">console.groq.com</a> prüfen.
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
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
