from config import RSS_FEEDS, YOUR_INTERESTS, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO
from fetcher import fetch_recent_items
from analyzer import analyze_items
from deduplicator import deduplicate_items
from mailer import format_html_email, format_error_email, send_email
from logger import build_log_entry, write_log
from health import update_feed_health
from datetime import datetime


if __name__ == "__main__":
    print("=== Daily Digest ===")
    today_str  = datetime.now().strftime("%d.%m.%Y")
    all_errors = []
    api_usage  = {"Gemini": 0, "Groq": 0}

    # ── 1. Fetch ──────────────────────────────────────────────────────────────
    print("\n[1/5] RSS-Feeds abrufen...")
    items, feed_statuses = fetch_recent_items(RSS_FEEDS)
    fetched_count = len(items)

    # ── 2. Feed health check ──────────────────────────────────────────────────
    print("\n[2/5] Feed-Gesundheit prüfen...")
    feed_warnings = update_feed_health(feed_statuses)
    if feed_warnings:
        print(f"      {len(feed_warnings)} Feed(s) haben den Fehlerschwellenwert erreicht.")

    if not fetched_count:
        print("Keine Artikel gefunden. Leere Zusammenfassung wird gesendet.")
        html = format_html_email([], feed_warnings=feed_warnings)
        send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
                   subject=f"Daily Digest - {today_str}")
        write_log(build_log_entry(0, 0, 0, [], api_usage, [], "success"))

    else:
        # ── 3. Analyze ────────────────────────────────────────────────────────
        print(f"\n[3/5] {fetched_count} Artikel zur Analyse senden...")
        analyzed, errors, batch_usage = analyze_items(items, YOUR_INTERESTS)
        all_errors.extend(errors)
        for api, count in batch_usage.items():
            api_usage[api] = api_usage.get(api, 0) + count

        filtered_count = len(analyzed)
        print(f"      {filtered_count} relevante Artikel nach dem Filtern.")

        # ── 4. Deduplicate ────────────────────────────────────────────────────
        print("\n[4/5] Duplikate entfernen...")
        analyzed, errors = deduplicate_items(analyzed)
        all_errors.extend(errors)
        deduped_count = len(analyzed)

        # ── 5. Format + Send + Log ────────────────────────────────────────────
        print("\n[5/5] E-Mail formatieren und senden...")

        if all_errors and deduped_count == 0:
            print("      Alle API-Aufrufe fehlgeschlagen. Sende Fehler-E-Mail...")
            html   = format_error_email(all_errors)
            status = "error"
            send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
                       subject=f"Daily Digest - FEHLER - {today_str}")
        else:
            html   = format_html_email(analyzed, feed_warnings=feed_warnings)
            status = "partial" if all_errors else "success"
            send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
                       subject=f"Daily Digest - {today_str}")

        print("\nLog schreiben...")
        log_entry = build_log_entry(
            fetched_count  = fetched_count,
            filtered_count = filtered_count,
            deduped_count  = deduped_count,
            analyzed_items = analyzed,
            api_usage      = api_usage,
            errors         = all_errors,
            status         = status,
        )
        write_log(log_entry)

    print("\nFertig.")
