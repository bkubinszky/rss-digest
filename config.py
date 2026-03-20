import os

# ─── RSS FEEDS ────────────────────────────────────────────────────────────────

RSS_FEEDS = [
    "https://www.trendingtopics.eu/feed/",
    "https://techcrunch.com/feed/",
    "https://t3n.de/rss.xml",
    "https://retail.at/feed/",
    "https://futurezone.at/xml/rss", 
    # Add as many as you like
]

# ─── INTERESTS ────────────────────────────────────────────────────────────────

YOUR_INTERESTS = """
The digest must be written entirely in German, regardless of the original language of the articles.
This includes all summaries and article titles. Translate everything into German.

I'm interested in:
- AI and technology, especially LLMs, AI agents, inference hardware (GPUs, LPUs), and developer tools
- European and Central European politics (Austria, Hungary, EU institutions)
- Investing, fintech, and SaaS (stocks, prediction markets, real estate investment tools)
- Business strategy, product management, and no-code/low-code tools

I am NOT interested in:
- Sports, celebrity gossip, entertainment news
- Generic lifestyle or health content
- US domestic politics unless it has strong EU or global market implications
"""

# ─── SCHEDULE ─────────────────────────────────────────────────────────────────
# NOTE: The actual cron schedule is set in .github/workflows/digest.yml
# Change it there. This comment is here so you know where to look.
# Current schedule: daily at 09:00 CET (08:00 UTC)

# ─── FETCH SETTINGS ───────────────────────────────────────────────────────────

FETCH_HOURS         = 24   # How many hours back to look for articles
SUMMARY_TRUNCATION  = 300  # Max characters of feed summary sent to LLM (keeps token usage low)

# ─── LLM SETTINGS ─────────────────────────────────────────────────────────────

GROQ_MODEL   = "llama-3.3-70b-versatile"
GEMINI_MODEL = "gemini-2.0-flash"
BATCH_SIZE   = 15  # Number of articles per LLM call
MAX_RETRIES  = 3   # Retry attempts per API call on transient errors
BACKOFF_BASE = 5   # Base seconds for exponential backoff (5s, 10s, 20s)

# ─── FILTERING ────────────────────────────────────────────────────────────────

SCORE_THRESHOLD = 5  # Articles scoring below this are excluded from the digest (1-10)

# ─── FEED HEALTH ──────────────────────────────────────────────────────────────

FAILURE_THRESHOLD = 3  # Consecutive fetch failures before a feed warning is shown in the digest

# ─── DEVELOPMENT ──────────────────────────────────────────────────────────────

MOCK_MODE = False  # Set to True to skip LLM calls and use fake data for testing

# ─── CREDENTIALS (from GitHub Secrets — never hardcode these) ─────────────────

EMAIL_FROM     = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_TO"]
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
