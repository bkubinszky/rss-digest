# Daily Digest v4 (simple)

A fully automated, free daily newsletter that fetches RSS feeds, filters and scores articles using AI, and delivers a clean link digest to your inbox every morning. No summaries — just the most relevant articles, ranked and ready to read.

## What it does

- Fetches articles from a configurable list of RSS feeds (last 24 hours)
- Sends items to an LLM for filtering and scoring only — no summaries generated
- Groups articles by source, ordered by relevance score descending
- Delivers a formatted HTML email daily with title, score, and link per article
- Automatically falls back to Groq if Gemini hits its daily token limit
- Sends a clear error email if both APIs fail
- Writes a structured run log to `log.json` after every run
- Tracks feed health and shows a warning banner if a feed has been failing for 3+ days
- Supports mock mode for testing without consuming any API tokens

## File structure

```
rss-digest/
├── digest.py        # Main orchestrator — runs the pipeline
├── config.py        # All configurable values: feeds, thresholds, model names, flags
├── interests.md     # Your interests and filters in plain English — edit this to tune the digest
├── fetcher.py       # RSS feed fetching
├── analyzer.py      # LLM calls (Gemini primary, Groq fallback), filtering and scoring only
├── mailer.py        # HTML email formatting and sending
├── logger.py        # Run logging to log.json
├── health.py        # Feed health tracking and warning logic
├── mock.py          # Pre-built fake results for token-free testing
├── log.json         # Auto-generated run history (committed by Actions bot)
├── feed_health.json # Auto-generated feed failure counters (committed by Actions bot)
└── .github/
    └── workflows/
        └── digest.yml  # GitHub Actions schedule and workflow
```

## Stack

| Component | Tool |
|---|---|
| Scheduling | GitHub Actions (free) |
| Primary LLM | Google Gemini 2.0 Flash (free tier) |
| Fallback LLM | Groq API — Llama 3.3 70B (free tier) |
| Email delivery | Gmail SMTP |

## Setup

### 1. API keys and credentials

- **Gemini API key**: [aistudio.google.com](https://aistudio.google.com)
- **Groq API key**: [console.groq.com](https://console.groq.com)
- **Gmail App Password**: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA enabled)

### 2. GitHub Secrets

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key |
| `GROQ_API_KEY` | Your Groq API key |
| `EMAIL_FROM` | Your Gmail address |
| `EMAIL_PASSWORD` | Your 16-character Gmail App Password |
| `EMAIL_TO` | Destination email address |

### 3. GitHub Actions permissions

Settings → Actions → General → Workflow permissions → **Read and write permissions**.

### 4. Configure the script

Edit `interests.md` to tune filtering — no Python required.

All other settings in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `FETCH_HOURS` | `24` | How many hours back to look for articles |
| `SUMMARY_TRUNCATION` | `300` | Max characters of feed summary sent to LLM |
| `BATCH_SIZE` | `15` | Number of articles per LLM call |
| `MAX_RETRIES` | `3` | Retry attempts per API call on transient errors |
| `BACKOFF_BASE` | `5` | Base seconds for exponential backoff |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `SOURCE_SCORE_THRESHOLD` | `8` | Show all articles per source scoring this or above |
| `SOURCE_MAX_ARTICLES` | `5` | Min articles shown per source if fewer score above threshold |
| `FAILURE_THRESHOLD` | `3` | Consecutive feed failures before a warning appears |
| `MOCK_MODE` | `False` | Set to `True` for token-free testing |

### 5. Schedule

Daily at **09:00 CET (08:00 UTC)**. Edit cron in `.github/workflows/digest.yml`:

```yaml
- cron: '0 8 * * *'
```

## Email format

Articles grouped by source, sources ordered by top article score descending.

Per source:
- All articles scoring `SOURCE_SCORE_THRESHOLD` (8) or above are shown
- If fewer than `SOURCE_MAX_ARTICLES` (5) score that high, top 5 shown regardless
- Each article: original title (linked), relevance score

## Mock mode

Set `MOCK_MODE = True` in `config.py` to test without consuming API tokens. Yellow banner appears in the email. Set back to `False` before the next scheduled run.

## Run log

```json
{
  "timestamp": "2026-03-22T08:01:23Z",
  "status": "success",
  "items": { "fetched": 77, "after_filter": 24, "after_dedup": 24 },
  "score_distribution": { "9-10": 4, "7-8": 12, "5-6": 8 },
  "api_usage": { "Gemini": 6, "Groq": 0 },
  "errors": []
}
```

## Free tier limits

| Service | Daily limit |
|---|---|
| Gemini 2.0 Flash (free) | 1,500 requests/day |
| Groq (free) | 100,000 tokens/day |

A single daily run uses roughly 6–7 API calls with a 5-second pause between batches to respect per-minute rate limits.

---

## ⚠️ Features implemented but not yet fully tested in production

**Retry with exponential backoff** (`analyzer.py`)
Retries failed LLM calls up to 3 times with increasing delays on transient errors. Will be confirmed the first time a real transient error occurs.

**Feed health check and warning** (`health.py`, `mailer.py`)
Tracks consecutive fetch failures in `feed_health.json`. After 3 failures a red warning banner appears. Not yet triggered in production.

---

## Backlog

### Content
- Optional summary mode — toggle summaries back on via `config.py` without switching branches
- Configurable summary length — short vs detailed
- Language toggle — German/English switchable
- Trending topics detection — flag recurring themes across 3+ articles
- Keyword watchlist — terms that boost an article's score automatically

### Feeds & delivery
- Newsletter integration via Kill the Newsletter
- OPML import support
- Skip sending if fewer than N articles pass filtering

### Visibility
- "First seen" indicator — flag articles from sources that rarely appear

---

## Changelog

### v4 (this branch: v4-simple)
- Removed summaries and "why it matters" entirely — LLM does filtering and scoring only
- Removed deduplication step
- Simplified email layout: title, score, link per article — no summary blocks
- Reduced `maxOutputTokens` from 4000 to 2000 (less output needed)
- Added 5-second inter-batch delay regardless of API used (fixes Gemini per-minute rate limit issue)
- `deduplicator.py` removed

### v3
- Redesigned email: articles grouped by source
- Top article per source: 2-sentence German summary + "why it matters" monetization note
- Gemini promoted to primary LLM; Groq demoted to fallback
- Article titles kept in original language
- Added `SOURCE_SCORE_THRESHOLD` and `SOURCE_MAX_ARTICLES`

### v2
- Refactored into modular file structure
- All configurable values centralized in `config.py`
- Interests moved to `interests.md`
- Gemini fallback, retry with backoff, error email, run logging, feed health tracking, mock mode

### v1
- Single-file implementation
- Groq-only, Gmail SMTP, German output, deduplication
