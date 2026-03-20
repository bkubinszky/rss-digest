# Daily Digest v2

A fully automated, free daily newsletter that fetches RSS feeds, filters and summarizes articles using AI, and delivers a clean digest to your inbox every morning.

## What it does

- Fetches articles from a configurable list of RSS feeds (last 24 hours)
- Sends items to an LLM for filtering, scoring, summarizing, and translation into German
- Merges duplicate stories from different sources into a single entry with multiple links
- Sorts articles by relevance score (highest first) and drops anything below 5/10
- Delivers a formatted HTML email daily
- Automatically falls back to Gemini if Groq hits its daily token limit
- Sends a clear error email if both APIs fail — no more silent empty digests
- Writes a structured run log to `log.json` after every run
- Supports mock mode for testing without consuming any API tokens

## File structure

```
rss-digest/
├── digest.py        # Main orchestrator — runs the pipeline
├── config.py        # Your feeds, interests, credentials, and mock flag
├── fetcher.py       # RSS feed fetching
├── analyzer.py      # LLM calls (Groq + Gemini fallback), filtering, scoring, summarizing
├── deduplicator.py  # Merges duplicate stories from different sources
├── mailer.py        # HTML email formatting and sending
├── logger.py        # Run logging to log.json
├── mock.py          # Pre-built fake results for token-free testing
├── log.json         # Auto-generated run history (committed by Actions bot)
└── .github/
    └── workflows/
        └── digest.yml  # GitHub Actions schedule and workflow
```

## Stack

| Component | Tool |
|---|---|
| Scheduling | GitHub Actions (free) |
| Primary LLM | Groq API — Llama 3.3 70B (free tier) |
| Fallback LLM | Google Gemini 2.0 Flash (free tier) |
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

Go to Settings → Actions → General → Workflow permissions and set to **Read and write permissions**. This is required for the Actions bot to commit `log.json` after each run.

### 4. Configure the script

In `config.py`, edit two sections:

**Your feeds:**
```python
RSS_FEEDS = [
    "https://yourfeed.com/rss",
    ...
]
```

**Your interests:**
```python
YOUR_INTERESTS = """
I'm interested in: ...
I am NOT interested in: ...
"""
```

The interests block is plain English — the more specific you are, the better the filtering and scoring will be.

### 5. Schedule

The digest runs daily at 07:00 UTC. To change the time, edit the cron line in `.github/workflows/digest.yml`:

```yaml
- cron: '0 7 * * *'
```

Use [crontab.guru](https://crontab.guru) to customize.

## Mock mode

To test the full pipeline without consuming any API tokens, set the following flag in `config.py`:

```python
MOCK_MODE = True
```

In mock mode, all LLM calls are skipped. Pre-built German-language fake articles from `mock.py` are used instead. The email, log, and everything else runs exactly as in a real run. Remember to set it back to `False` before the next scheduled run.

## Manual test run

Go to Actions → Daily RSS Digest → Run workflow. Check the logs for any errors. Avoid running multiple manual tests in a single day — each real run consumes roughly 20,000–25,000 Groq tokens and you may hit the daily limit before the scheduled run. Use mock mode instead.

## Run log

After each run, `log.json` is automatically updated and committed to the repo by the Actions bot. Each entry looks like this:

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

A single daily run consumes roughly 20,000–25,000 Groq tokens. Both limits are well within range for normal use. Use mock mode during development and testing.

## Changelog

### v2
- Refactored into modular file structure (`config`, `fetcher`, `analyzer`, `deduplicator`, `mailer`, `logger`, `mock`)
- Added Gemini 2.0 Flash as automatic fallback when Groq rate limit is hit
- Added descriptive error email when both APIs fail
- Added run logging to `log.json`, committed automatically after each run
- Added mock mode for token-free testing
- Reduced feed summary truncation from 600 to 300 characters to lower token usage
- Articles scoring below 5/10 are excluded from the digest

### v1
- Single-file implementation
- Groq-only LLM with batched processing
- Gmail SMTP delivery
- German-language output with title translation
- Deduplication with merged source links
