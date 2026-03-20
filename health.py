import json
import os
from config import FAILURE_THRESHOLD

HEALTH_FILE = "feed_health.json"


def load_health():
    """Load existing feed health data, or return empty dict if file doesn't exist."""
    if os.path.exists(HEALTH_FILE):
        try:
            with open(HEALTH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_health(health):
    """Write feed health data to disk."""
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(health, f, ensure_ascii=False, indent=2)


def update_feed_health(feed_statuses):
    """Update consecutive failure counters for each feed.

    Returns:
        warnings: list of dicts for feeds that have hit the failure threshold
                  each dict has: {url, source, consecutive_failures}
    """
    health   = load_health()
    warnings = []

    for url, status in feed_statuses.items():
        source = status.get("source", url)

        if status["success"]:
            if url in health:
                if health[url]["consecutive_failures"] >= FAILURE_THRESHOLD:
                    print(f"      Feed recovered: {source}")
                del health[url]
        else:
            if url not in health:
                health[url] = {"source": source, "consecutive_failures": 0}

            health[url]["consecutive_failures"] += 1
            failures = health[url]["consecutive_failures"]
            print(f"      Feed failure {failures}/{FAILURE_THRESHOLD}: {source}")

            if failures >= FAILURE_THRESHOLD:
                warnings.append({
                    "url":                  url,
                    "source":               source,
                    "consecutive_failures": failures,
                })

    save_health(health)
    return warnings
