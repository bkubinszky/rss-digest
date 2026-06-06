import os

# ─── RSS FEEDS ────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    "https://www.trendingtopics.eu/feed/",
    "https://techcrunch.com/feed/",
    "https://t3n.de/rss.xml",
    "https://retail.at/feed/",
    "https://futurezone.at/xml/rss",
    "https://www.derstandard.at/rss/web",
    "https://www.derstandard.at/rss/zukunft",
    # Add as many as you like
]

# ─── INTERESTS ────────────────────────────────────────────────────────────────
# Edit interests.md directly in GitHub — no need to touch Python files.

YOUR_INTERESTS = os.environ["YOUR_INTERESTS"]

# ─── SCHEDULE ─────────────────────────────────────────────────────────────────
# NOTE: The actual cron schedule is set in .github/workflows/digest.yml
# Change it there. Current schedule: daily at 05:30 CET (04:30 UTC)

# ─── FETCH SETTINGS ───────────────────────────────────────────────────────────

FETCH_HOURS        = 24   # How many hours back to look for articles
SUMMARY_TRUNCATION = 300  # Max characters of feed summary sent to LLM

# ─── LLM SETTINGS ─────────────────────────────────────────────────────────────

GEMINI_MODEL = "gemini-2.0-flash"
GROQ_MODEL   = "llama-3.3-70b-versatile"
BATCH_SIZE   = 15  # Number of articles per LLM call
MAX_RETRIES  = 3   # Retry attempts per API call on transient errors
BACKOFF_BASE = 5   # Base seconds for exponential backoff (5s, 10s, 20s)

# ─── FILTERING & DISPLAY ──────────────────────────────────────────────────────

SOURCE_SCORE_THRESHOLD = 8  # Show all articles per source scoring this or above
SOURCE_MAX_ARTICLES    = 5  # If fewer than SOURCE_MAX_ARTICLES score above threshold,
                            # show top SOURCE_MAX_ARTICLES regardless of score

# ─── FEED HEALTH ──────────────────────────────────────────────────────────────

FAILURE_THRESHOLD = 3  # Consecutive fetch failures before a warning appears in the digest

# ─── DEVELOPMENT ──────────────────────────────────────────────────────────────

MOCK_MODE = False  # Set to True to skip LLM calls and use fake data for testing

# ─── CREDENTIALS (from GitHub Secrets — never hardcode these) ─────────────────

EMAIL_FROM     = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_TO"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]
