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

# ─── CREDENTIALS (from GitHub Secrets — never hardcode these) ─────────────────

EMAIL_FROM     = os.environ["EMAIL_FROM"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO       = os.environ["EMAIL_TO"]
GROQ_API_KEY   = os.environ["GROQ_API_KEY"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
