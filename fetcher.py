import feedparser
from datetime import datetime, timezone, timedelta


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

                if published is None or published >= cutoff:
                    items.append({
                        "title":     entry.get("title", "No title"),
                        "link":      entry.get("link", ""),
                        "summary":   entry.get("summary", "")[:300],
                        "published": published.isoformat() if published else "unknown",
                        "source":    source_name,
                    })

        except Exception as e:
            print(f"Warning: failed to parse feed {url}: {e}")

    print(f"Fetched {len(items)} total items from {len(feeds)} feeds.")
    return items
