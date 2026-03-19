from config import RSS_FEEDS, YOUR_INTERESTS, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO
from fetcher import fetch_recent_items
from analyzer import analyze_items
from deduplicator import deduplicate_items
from mailer import format_html_email, format_error_email, send_email
from logger import build_log_entry, write_log
from datetime import datetime


if __name__ == "__main__":
    print("=== Daily Digest ===")
    today_str  = datetime.now().strftime("%d.%m.%Y")
    all_errors = []
    api_usage  = {"Groq": 0, "Gemini": 0}

    # ── 1. Fetch ──────────────────────────────────────────────────────────────
    print("\n[1/4] RSS-Feeds abrufen...")
    items = fetch_recent_items(RSS_FEEDS, hours=24)
    fetched_count = len(items)

    if not fetched_count:
        print("Keine Artikel gefunden. Leere Zusammenfassung wird gesendet.")
        html = format_html_email([])
        send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
                   subject=f"Daily Digest - {today_str}")
        write_log(build_log_entry(0, 0, 0, [], api_usage, [], "success"))

    else:
        # ── 2. Analyze ────────────────────────────────────────────────────────
        print(f"\n[2/4] {fetched_count} Artikel zur Analyse senden...")
        analyzed, errors, batch_usage = analyze_items(items, YOUR_INTERESTS)
        all_errors.extend(errors)
        for api, count in batch_usage.items():
            api_usage[api] = api_usage.get(api, 0) + count

        analyzed = [i for i in analyzed if i.get("score", 0) >= 5]
        filtered_count = len(analyzed)
        print(f"      {filtered_count} relevante Artikel nach dem Filtern.")

        # ── 2b. Deduplicate ───────────────────────────────────────────────────
        print("\n[2b/4] Duplikate entfernen...")
        analyzed, errors = deduplicate_items(analyzed)
        all_errors.extend(errors)
        deduped_count = len(analyzed)

        # ── 3. Format ─────────────────────────────────────────────────────────
        print("\n[3/4] HTML-E-Mail formatieren...")

        if all_errors and deduped_count == 0:
            print("      Alle API-Aufrufe fehlgeschlagen. Sende Fehler-E-Mail...")
            html   = format_error_email(all_errors)
            status = "error"
            send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
                       subject=f"Daily Digest - FEHLER - {today_str}")
        else:
            html   = format_html_email(analyzed)
            status = "partial" if all_errors else "success"
            send_email(html, EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD,
                       subject=f"Daily Digest - {today_str}")

        # ── 4. Log ────────────────────────────────────────────────────────────
        print("\n[4/4] Log schreiben...")
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
