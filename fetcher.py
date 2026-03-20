import feedparser
from datetime import datetime, timezone, timedelta
from config import FETCH_HOURS, SUMMARY_TRUNCATION


def fetch_recent_items(feeds, hours=FETCH_HOURS):
    """Fetch all feed entries published within the last N hours.

    Returns:
        items: list of article dicts
        feed_statuses: dict of {url: {"source": str, "success": bool, "error": str or None}}
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    items = []
    feed_statuses = {}

    for url in feeds:
        try:
            feed = feedparser.parse(url)
            source_name = feed.feed.get("title", url)

            if feed.bozo and not feed.entries:
                raise ValueError(f"Feed parse error: {feed.bozo_exception}")

            feed_items = []
            for entry in feed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except Exception:
                        pass

                if published is None or published >= cutoff:
                    feed_items.append({
                        "title":     entry.get("title", "No title"),
                        "link":      entry.get("link", ""),
                        "summary":   entry.get("summary", "")[:SUMMARY_TRUNCATION],
                        "published": published.isoformat() if published else "unknown",
                        "source":    source_name,
                    })

            items.extend(feed_items)
            feed_statuses[url] = {"source": source_name, "success": True, "error": None}

        except Exception as e:
            source_name = url
            print(f"Warning: failed to parse feed {url}: {e}")
            feed_statuses[url] = {"source": source_name, "success": False, "error": str(e)}

    total      = len(items)
    successful = sum(1 for s in feed_statuses.values() if s["success"])
    print(f"Fetched {total} total items from {successful}/{len(feeds)} feeds successfully.")
    return items, feed_statuses
