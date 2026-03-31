# Daily Digest v4

A fully automated, free daily newsletter that fetches RSS feeds, filters and scores articles using AI, and delivers a clean link digest to your inbox every morning. No summaries — just the most relevant articles, ranked and ready to read.

## What it does

- Fetches articles from a configurable list of RSS feeds (last 24 hours)
- Sends items to an LLM for filtering and scoring only — no summaries generated
- Groups articles by source, ordered by relevance score descending
- Delivers a clean editorial HTML email daily with title, score, and link per article
- Automatically falls back to Groq if Gemini hits its daily token limit
- Sends a clear error email if both APIs fail
- Tracks feed health and shows a warning banner if a feed has been failing for 3+ days
- Supports mock mode for testing without consuming any API tokens

## File structure

```
rss-digest/
├── digest.py          # Main orchestrator — runs the pipeline
├── config.py          # All configurable values: feeds, thresholds, model names, flags
├── fetcher.py         # RSS feed fetching
├── analyzer.py        # LLM calls (Gemini primary, Groq fallback), filtering and scoring only
├── mailer.py          # HTML email formatting and sending
├── logger.py          # Run logging (stdout only — not committed to repo)
├── health.py          # Feed health tracking and warning logic
├── mock.py            # Pre-built fake results for token-free testing
├── requirements.txt   # Pinned Python dependencies
├── .gitignore         # Excludes .env, __pycache__, and runtime log files
└── .github/
    └── workflows/
        └── digest.yml # GitHub Actions schedule and workflow
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
| `YOUR_INTERESTS` | Full text of your interests and filters |

### 3. Configure the script

Edit the `YOUR_INTERESTS` GitHub Secret to tune filtering — go to Settings → Secrets and variables → Actions, find `YOUR_INTERESTS`, and update the value.

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

### 4. Schedule

Daily at **05:30 CEST (03:30 UTC)**. Edit cron in `.github/workflows/digest.yml`:

```yaml
- cron: '30 3 * * *'
```

Use [crontab.guru](https://crontab.guru) to customize. Note: GitHub Actions does not handle daylight saving time — expect a 1-hour drift between CET and CEST seasons.

## Email format

Articles grouped by source, sources ordered by top article score descending.

Per source:
- All articles scoring `SOURCE_SCORE_THRESHOLD` (8) or above are shown
- If fewer than `SOURCE_MAX_ARTICLES` (5) score that high, top 5 shown regardless
- Each article: original title (linked), relevance score pill (green / amber / grey)

## Mock mode

Set `MOCK_MODE = True` in `config.py` to test without consuming API tokens. A yellow banner appears in the email. Set back to `False` before the next scheduled run.

## Free tier limits

| Service | Daily limit |
|---|---|
| Gemini 2.0 Flash (free) | 1,500 requests/day |
| Groq (free) | 100,000 tokens/day |

A single daily run uses roughly 6–7 API calls with a 5-second pause between batches to respect per-minute rate limits.

---

## Security notes

- All credentials are loaded from GitHub Secrets via environment variables — never hardcoded
- Gemini API key is sent as a request header (`x-goog-api-key`), not as a URL query string
- All user-sourced strings (titles, source names, feed warnings) are HTML-escaped before rendering
- All URLs are validated to `http`/`https` only before insertion into email HTML
- Python dependencies are pinned in `requirements.txt`
- Workflow runs with `contents: read` permissions (minimum required)
- `.env` is excluded from commits via `.gitignore`
- Runtime logs (`log.json`, `feed_health.json`) are not committed to the repo — check the GitHub Actions run logs instead

---

## ⚠️ Features implemented but not yet fully tested in production

**Retry with exponential backoff** (`analyzer.py`)
Retries failed LLM calls up to 3 times with increasing delays on transient errors. Will be confirmed the first time a real transient error occurs.

**Feed health check and warning** (`health.py`, `mailer.py`)
Tracks consecutive fetch failures. After 3 failures a red warning banner appears in the digest. Not yet triggered in production.

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

### v4 (current)
- Removed summaries and "why it matters" entirely — LLM does filtering and scoring only
- Removed deduplication step
- Redesigned email: clean editorial layout inspired by The Editorial Ledger — italic serif header, uppercase source names, score pills, minimal borders
- All user-sourced content HTML-escaped; URLs validated to http/https only
- Gemini API key moved from URL query string to request header
- Python dependencies pinned in `requirements.txt`
- Workflow scoped to `contents: read` permissions
- Runtime logs no longer committed to repo — available in GitHub Actions run logs
- Added 5-second inter-batch delay to respect Gemini per-minute rate limits
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

---

## Disclaimer

This repository is provided for informational and experimental purposes only. The code is offered "as is", without any warranties of any kind, express or implied. I make no guarantees regarding its correctness, reliability, or suitability for any purpose. Use of this code is entirely at your own risk. I assume no responsibility or liability for any damages, losses, or issues arising from its use, misuse, or inability to use the contents of this repository.
