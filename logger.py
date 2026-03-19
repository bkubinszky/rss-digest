import json
import os
from datetime import datetime

LOG_FILE = "log.json"


def write_log(entry):
    """Append a run entry to log.json. Creates the file if it doesn't exist.
    
    IMPORTANT: This file contains only metadata — no credentials, no email
    addresses, no API keys, no article content. Safe to commit to the repo.
    """
    logs = []

    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except (json.JSONDecodeError, IOError):
            logs = []

    logs.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    print(f"Log entry written to {LOG_FILE}.")


def build_log_entry(
    fetched_count,
    filtered_count,
    deduped_count,
    analyzed_items,
    api_usage,
    errors,
    status
):
    """Build a structured log entry for one run. Contains NO sensitive data."""

    # Score distribution
    scores = [item.get("score", 0) for item in analyzed_items]
    score_dist = {
        "9-10": sum(1 for s in scores if s >= 9),
        "7-8":  sum(1 for s in scores if 7 <= s <= 8),
        "5-6":  sum(1 for s in scores if 5 <= s <= 6),
    }

    return {
        "timestamp":       datetime.utcnow().isoformat() + "Z",
        "status":          status,  # "success", "partial", "error"
        "items": {
            "fetched":     fetched_count,
            "after_filter": filtered_count,
            "after_dedup": deduped_count,
        },
        "score_distribution": score_dist,
        "api_usage":       api_usage,  # e.g. {"Groq": 4, "Gemini": 1}
        "errors":          errors,     # list of error strings, empty if clean run
    }
