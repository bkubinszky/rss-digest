# Daily Digest v2

A fully automated, free daily newsletter that fetches RSS feeds, filters and summarizes articles using AI, and delivers a clean digest to your inbox every morning.

## What it does

- Fetches articles from a configurable list of RSS feeds (last 24 hours)
- Sends items to an LLM for filtering, scoring, summarizing, and translation into German
- Merges duplicate stories from different sources into a single entry with multiple links
- Sorts articles by relevance score (highest first) and drops anything below the configured threshold
- Delivers a formatted HTML email daily
- Automatically falls back to Gemini if Groq hits its daily token limit
- Sends a clear error email if both APIs fail — no more silent empty digests
- Writes a structured run log to `log.json` after every run
- Tracks feed health and shows a warning banner in the digest if a feed has been failing for 3+ days
- Supports mock mode for testing without consuming any API tokens

## File structure

```
rss-digest/
├── digest.py        # Main orchestrator — runs the pipeline
├── config.py        # All configurable values: feeds, interests, thresholds, model names, flags
├── fetcher.py       # RSS feed fetching
├── analyzer.py      # LLM calls (Groq + Gemini fallback), filtering, scoring, summarizing
├── deduplicator.py  # Merges duplicate stories from different sources
├── mailer.py        # HTML email formatting and sending
├── logger.py        # Run logging to log.json
├── health.py        # Feed health tracking and warning logic
├── mock.py          # Pre-built fake results for token-free testing
├── log.json         # Auto-generated run history (committed by Actions bot)
├── feed_health.json # Auto-generated feed failure counters (committed by Actions bot)
├── .gitignore       # Excludes Python cache files and local .env from commits
└── .github/
    └── workflows/
        └── digest.yml  # GitHub Actions schedule and workflow
```

## Stack

| Component | Tool |
|---|---|
| Scheduling | GitHub Actions (free) |
| Primary LLM |  Google Gemini 2.0 Flash (free tier) |
| Fallback LLM | Groq API — Llama 3.3 70B (free tier) |
| Email delivery | Gmail SMTP |

If Groq hits its daily token limit, the script automatically retries with Gemini. If both fail, you receive a descriptive error email instead of a silent empty digest.

## Setup

### 1. API keys and credentials

- **Groq API key**: [console.groq.com](https://console.groq.com)
- **Gemini API key**: [aistudio.google.com](https://aistudio.google.com)
- **Gmail App Password**: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA enabled)

### 2. GitHub Secrets

Add the following secrets under Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GEMINI_API_KEY` | Your Gemini API key |
| `EMAIL_FROM` | Your Gmail address |
| `EMAIL_PASSWORD` | Your 16-character Gmail App Password |
| `EMAIL_TO` | Destination email address |

### 3. GitHub Actions permissions

Go to Settings → Actions → General → Workflow permissions and set to **Read and write permissions**. This is required for the Actions bot to commit `log.json` and `feed_health.json` after each run.

### 4. Configure the script

All configurable values live in `config.py`. Key settings:

| Setting | Default | Description |
|---|---|---|
| `RSS_FEEDS` | — | Your list of RSS feed URLs |
| `YOUR_INTERESTS` | — | Plain English description of your interests and filters |
| `FETCH_HOURS` | `24` | How many hours back to look for articles |
| `SUMMARY_TRUNCATION` | `300` | Max characters of feed summary sent to LLM |
| `BATCH_SIZE` | `15` | Number of articles per LLM call |
| `MAX_RETRIES` | `3` | Retry attempts per API call on transient errors |
| `BACKOFF_BASE` | `5` | Base seconds for exponential backoff |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `SCORE_THRESHOLD` | `5` | Articles scoring below this are excluded (1–10) |
| `FAILURE_THRESHOLD` | `3` | Consecutive feed failures before a warning appears |
| `MOCK_MODE` | `False` | Set to `True` for token-free testing |

### 5. Schedule

The digest runs daily at **09:00 CET (08:00 UTC)**. GitHub Actions always uses UTC. To change the time, edit the cron line in `.github/workflows/digest.yml`:

```yaml
- cron: '0 8 * * *'
```

Use [crontab.guru](https://crontab.guru) to customize. Note: GitHub Actions does not handle daylight saving time automatically — expect a 1-hour drift between CET and CEST seasons.

## Mock mode

To test the full pipeline without consuming any API tokens, set in `config.py`:

```python
MOCK_MODE = True
```

In mock mode, all LLM calls are skipped and pre-built German-language fake articles from `mock.py` are used instead. The email will show a yellow warning banner indicating mock data. Remember to set it back to `False` before the next scheduled run.

## Run log

After each run, `log.json` is automatically updated and committed by the Actions bot. Each entry looks like this:

```json
{
  "timestamp": "2026-03-19T07:01:23Z",
  "status": "success",
  "items": { "fetched": 68, "after_filter": 21, "after_dedup": 18 },
  "score_distribution": { "9-10": 3, "7-8": 9, "5-6": 6 },
  "api_usage": { "Groq": 5, "Gemini": 0 },
  "errors": []
}
```

`status` is one of `success`, `partial` (some batches failed but a digest was still sent), or `error` (all API calls failed, error email sent).

## Free tier limits

| Service | Daily limit |
|---|---|
| Groq (free) | 100,000 tokens/day |
| Gemini 2.0 Flash (free) | 1,500 requests/day |

A single daily run consumes roughly 20,000–25,000 Groq tokens. Both limits are well within range for normal use. Use mock mode during development and testing to avoid burning through the daily quota.

### Local development
If you ever run the script locally, create a `.env` file in the repo root with your credentials instead of setting them as shell environment variables. This file is excluded from commits via `.gitignore` — never commit it.

---

## ⚠️ Features implemented but not yet tested in production

The following features were built and committed but could not be fully verified due to the nature of what would be required to trigger them:

**Retry with exponential backoff** (`analyzer.py`)
Automatically retries failed LLM calls up to 3 times with increasing delays (5s, 10s, 20s) on transient network errors or server-side 5xx responses. Cannot be easily triggered on demand — will be confirmed working the first time a real transient error occurs in production.

**Feed health check and warning** (`health.py`, `mailer.py`)
Tracks consecutive fetch failures per feed in `feed_health.json`. After 3 consecutive failures, a red warning banner appears in the next digest email listing the affected feeds. Resets automatically when a feed recovers. Requires a feed to fail 3 days in a row to observe — has not yet been triggered in production.

---

## Backlog

### Content
- Change content to Lists of article (with original title and link) by source, and only 1 article of every source should be summarized. The 1 article for summarization should be the possibly most actionable in terms of monetization for me.  
- "Why this matters" field — one extra sentence of context per article explaining its broader relevance
- Configurable summary length — short (1 sentence) vs detailed (3–4 sentences), switchable in `config.py`
- Language toggle — switch output between German and English without rewriting the interests block
- Trending topics detection — if the same theme appears across 3+ articles, flag it at the top of the digest
- Keyword watchlist — a list of terms that automatically boost an article's score if they appear

### Feeds & delivery
- Newsletter integration via Kill the Newsletter — convert email newsletters to RSS feeds
- OPML import support — import feed list directly from any RSS reader export
- Skip sending if below minimum threshold — if fewer than N articles score above the threshold, skip the email entirely

### Visibility
- "First seen" indicator — flag articles from sources that rarely appear in the digest

### Configuration
- Move `YOUR_INTERESTS` to a separate `interests.md` file — easier to edit in GitHub without touching Python

---

## Changelog

### v2
- Refactored into modular file structure (`config`, `fetcher`, `analyzer`, `deduplicator`, `mailer`, `logger`, `health`, `mock`)
- All configurable values centralized in `config.py`
- Added Gemini 2.0 Flash as automatic fallback when Groq rate limit is hit
- Added retry with exponential backoff for transient errors
- Added descriptive error email when both APIs fail
- Added run logging to `log.json`, committed automatically after each run
- Added feed health tracking with warning banner in digest email
- Added mock mode for token-free testing with visual banner in email
- Reduced feed summary truncation from 600 to 300 characters to lower token usage
- Articles scoring below threshold excluded from digest (configurable)
- Schedule set to 09:00 CET daily

### v1
- Single-file implementation
- Groq-only LLM with batched processing
- Gmail SMTP delivery
- German-language output with title translation
- Deduplication with merged source links
