# Findly 🚀

Findly (formerly Wallatrack) is a high-efficiency Telegram bot and Web Dashboard that helps you track items on **Wallapop** and **Vinted** simultaneously. It alerts you via Telegram the moment a new item matching your criteria is posted.

## Features
- **Multi-platform tracking**: Search Wallapop and Vinted.
- **Modern Web UI**: Manage everything from a sleek Single Page Application (Dashboard, Searches, and Settings).
- **Quick Add via URL**: Paste a Wallapop or Vinted URL directly in the Web UI or Telegram to auto-fill the search criteria.
- **Anti-ban Resilience (No Proxies needed by default)**:
  - **User-Agent Spoofing**: Automatic rotation of real browser user-agents.
  - **Cookie Warming**: Background ghost requests to bypass initial security checks.
  - **Auto-Retries**: Automatic session reset and retry logic when API endpoints return 401/403 blocks.
  - **Smart Jitter**: Randomized polling intervals to avoid detectable automated patterns.
- **Asynchronous Queues**: The scraping loop is decoupled from Telegram notifications, ensuring lightning-fast scans even if Telegram rate limits are hit.
- **Inline Management**: Unfollow searches directly from the Telegram notification using inline buttons.

## Setup Instructions

1. Clone this repository.
2. Run with Docker Compose (No `.env` file required for basic startup!):

```bash
docker-compose up -d --build
```

3. Navigate to the Web UI at `http://localhost:8000`.
4. Go to the **Settings** tab in the Web UI to configure your `Telegram Bot Token` and `Allowed Chat IDs`. The bot will automatically restart and apply the settings.

## Usage

**Via Web UI (Recommended)**:
Navigate to `http://localhost:8000` to view statistics, add new tracking queries, manual refresh, and review a history of seen items.

**Via Telegram**:
- `/start` to see the welcome message.
- `/add <keywords> [min_price] [max_price] [distance_in_km]`
- Paste a Wallapop or Vinted URL directly to track it.
- `/list` to view your active searches.
- `/delete <id>` to remove a search.
