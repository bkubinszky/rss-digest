# Daily Digest v3

A fully automated, free daily newsletter that fetches RSS feeds, filters and summarizes articles using AI, and delivers a clean digest to your inbox every morning.

## What it does

- Fetches articles from a configurable list of RSS feeds (last 24 hours)
- Sends items to an LLM for filtering, scoring, and analysis
- Groups articles by source, sorted by relevance score
- Top article per source gets a 2-sentence German summary and a "why it matters" monetization note
- All other articles listed with original title and link only
- Merges duplicate stories from different sources into a single entry with multiple links
- Delivers a formatted HTML email daily
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
├── analyzer.py      # LLM calls (Gemini primary, Groq fallback), filtering, scoring, summarizing
├── deduplicator.py  # Merges duplicate stories from different sources
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

If Gemini hits its daily token limit, the script automatically retries with Groq. If both fail, you receive a descriptive error email instead of a silent empty digest.

## Setup

### 1. API keys and credentials

- **Gemini API key**: [aistudio.google.com](https://aistudio.google.com)
- **Groq API key**: [console.groq.com](https://console.groq.com)
- **Gmail App Password**: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA enabled)

### 2. GitHub Secrets

Add the following secrets under Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key |
| `GROQ_API_KEY` | Your Groq API key |
| `EMAIL_FROM` | Your Gmail address |
| `EMAIL_PASSWORD` | Your 16-character Gmail App Password |
| `EMAIL_TO` | Destination email address |

### 3. GitHub Actions permissions

Go to Settings → Actions → General → Workflow permissions and set to **Read and write permissions**. Required for the Actions bot to commit `log.json` and `feed_health.json` after each run.

### 4. Configure the script

Edit `interests.md` directly in GitHub to tune what gets filtered and summarized — no Python required.

All other configurable values live in `config.py`:

| Setting | Default | Description |
|---|---|---|
| `YOUR_INTERESTS` | — | Loaded automatically from `interests.md` |
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

The digest runs daily at **09:00 CET (08:00 UTC)**. To change the time, edit the cron line in `.github/workflows/digest.yml`:

```yaml
- cron: '0 8 * * *'
```

Use [crontab.guru](https://crontab.guru) to customize. Note: GitHub Actions does not handle daylight saving time — expect a 1-hour drift between CET and CEST seasons.

## Email format

Articles are grouped by source. Sources are ordered by their top article's score descending.

Per source:
- All articles scoring `SOURCE_SCORE_THRESHOLD` (8) or above are shown
- If fewer than `SOURCE_MAX_ARTICLES` (5) score that high, the top 5 are shown regardless
- **Top article**: original title, score, 2-sentence German summary, "why it matters" monetization note, source link(s)
- **Other articles**: original title, score, link only

## Mock mode

Set `MOCK_MODE = True` in `config.py` to skip all LLM calls and use pre-built fake data from `mock.py`. The email will show a yellow warning banner. Remember to set it back to `False` before the next scheduled run.

## Run log

After each run, `log.json` is automatically updated and committed. Each entry:

```json
{
  "timestamp": "2026-03-20T08:01:23Z",
  "status": "success",
  "items": { "fetched": 68, "after_filter": 21, "after_dedup": 18 },
  "score_distribution": { "9-10": 3, "7-8": 9, "5-6": 6 },
  "api_usage": { "Gemini": 5, "Groq": 0 },
  "errors": []
}
```

`status` is one of `success`, `partial`, or `error`.

## Free tier limits

| Service | Daily limit |
|---|---|
| Gemini 2.0 Flash (free) | 1,500 requests/day |
| Groq (free) | 100,000 tokens/day |

A single daily run uses roughly 6–8 API calls. Both limits are well within range for normal use. Use mock mode during development.

---

## ⚠️ Features implemented but not yet fully tested in production

**Retry with exponential backoff** (`analyzer.py`)
Retries failed LLM calls up to 3 times with increasing delays on transient network errors or 5xx responses. Will be confirmed working the first time a real transient error occurs.

**Feed health check and warning** (`health.py`, `mailer.py`)
Tracks consecutive fetch failures per feed in `feed_health.json`. After 3 failures, a red warning banner appears in the digest. Requires a feed to fail 3 days in a row to trigger — not yet observed in production.

---

## Backlog

### Content
- Configurable summary length — short (1 sentence) vs detailed (3–4 sentences), switchable in `config.py`
- Language toggle — switch output between German and English without rewriting interests
- Trending topics detection — flag recurring themes across 3+ articles at the top of the digest
- Keyword watchlist — terms that automatically boost an article's score

### Feeds & delivery
- Newsletter integration via Kill the Newsletter
- OPML import support — import feed list from any RSS reader export
- Skip sending if below minimum threshold — if fewer than N articles pass filtering, skip the email

### Visibility
- "First seen" indicator — flag articles from sources that rarely appear

---

## Changelog

### v3
- Redesigned email format: articles grouped by source, ordered by top article score
- Top article per source: original title, score, 2-sentence German summary, "why it matters" monetization note
- All other articles: original title, score, link only
- Gemini promoted to primary LLM (better multilingual quality); Groq demoted to fallback
- Removed global score filter — display logic now handled per source in email formatter
- Added `SOURCE_SCORE_THRESHOLD` and `SOURCE_MAX_ARTICLES` to `config.py`
- Article titles kept in original language (no translation)
- Updated mock data to match new structure

### v2
- Refactored into modular file structure
- All configurable values centralized in `config.py`
- Interests moved to `interests.md`
- Added Groq as automatic fallback when Gemini rate limit is hit
- Added retry with exponential backoff for transient errors
- Added descriptive error email when both APIs fail
- Added run logging to `log.json`
- Added feed health tracking with warning banner
- Added mock mode with visual banner
- Schedule set to 09:00 CET daily

### v1
- Single-file implementation
- Groq-only LLM with batched processing
- Gmail SMTP delivery
- German-language output with title translation
- Deduplication with merged source links
