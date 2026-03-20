import json
from analyzer import call_llm, clean_json

def deduplicate_items(items):
    from config import MOCK_MODE
    from mock import MOCK_DEDUPED_ITEMS
    if MOCK_MODE:
        print("      MOCK MODE: skipping deduplication LLM call, returning mock data.")
        return MOCK_DEDUPED_ITEMS, []
        
    """Merge items covering the same story into one entry with multiple links."""
    if not items:
        return [], []

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
        raw, api_used = call_llm(prompt, label="deduplication")
        print(f"      (answered by {api_used})")
        deduped = json.loads(clean_json(raw))
        print(f"      {len(items)} items -> {len(deduped)} after deduplication.")
        return deduped, []

    except RuntimeError as e:
        print(f"      ERROR: deduplication failed: {e}")
        return items, [f"Deduplication: {e}"]

    except json.JSONDecodeError as e:
        print(f"      Warning: deduplication returned malformed JSON: {e}")
        return items, []
