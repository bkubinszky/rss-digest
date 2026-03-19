# Daily Digest

A fully automated, free daily newsletter that fetches RSS feeds, filters and summarizes articles using AI, and delivers a clean digest to your inbox every morning.

## What it does

- Fetches articles from a configurable list of RSS feeds (last 24 hours)
- Sends items to an LLM for filtering, scoring, summarizing, and translation into German
- Merges duplicate stories from different sources into a single entry with multiple links
- Sorts articles by relevance score (highest first) and drops anything below 5/10
- Delivers a formatted HTML email daily

## Stack

| Component | Tool |
|---|---|
| Scheduling | GitHub Actions (free) |
| Primary LLM | Groq API — Llama 3.3 70B (free tier) |
| Fallback LLM | Google Gemini 1.5 Flash (free tier) |
| Email delivery | Gmail SMTP |

If Groq hits its daily token limit, the script automatically retries with Gemini. If both fail, you receive an error email with a clear explanation instead of a silent empty digest.

## Setup

### 1. API keys and credentials

- **Groq API key**: [console.groq.com](https://console.groq.com)
- **Gemini API key**: [aistudio.google.com](https://aistudio.google.com)
- **Gmail App Password**: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (requires 2FA enabled)

### 2. GitHub Secrets

Add the following secrets to your repo under Settings → Secrets and variables → Actions:

| Secret | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GEMINI_API_KEY` | Your Gemini API key |
| `EMAIL_FROM` | Your Gmail address |
| `EMAIL_PASSWORD` | Your 16-character Gmail App Password |
| `EMAIL_TO` | Destination email address |

### 3. Configure the script

In `digest.py`, edit two sections:

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

The interests block is plain English — the more specific you are, the better the filtering.

### 4. Schedule

The digest runs daily at 05:00 UTC. To change the time, edit the cron line in `.github/workflows/digest.yml`:

```yaml
- cron: '0 5 * * *'
```

Use [crontab.guru](https://crontab.guru) to customize.

## Manual test run

Go to Actions → Daily RSS Digest → Run workflow. Check the logs for any errors.

## Free tier limits

| Service | Daily limit |
|---|---|
| Groq (free) | 100,000 tokens/day |
| Gemini 1.5 Flash (free) | 1,500 requests/day |

A single daily run consumes roughly 20,000-25,000 Groq tokens. Both limits are well within range for normal use. Avoid running multiple manual tests in a single day to prevent hitting the Groq limit before the scheduled run.
