# Findly 🚀

Findly (formerly Wallatrack) is a high-efficiency Telegram bot that helps you track items on **Wallapop** and **Vinted** simultaneously. It alerts you the moment a new item matching your criteria is posted.

## Features
- **Multi-platform tracking**: Search Wallapop and Vinted.
- **Anti-ban Resilience**: Built-in proxy and User-Agent rotation, along with automatic session resets on Cloudflare blocks.
- **Asynchronous Queues**: The scraping loop is decoupled from Telegram notifications, ensuring lightning-fast scans even if Telegram rate limits are hit.
- **Inline Management**: Unfollow searches directly from the notification using inline buttons.

## Setup Instructions

1. Clone this repository.
2. Create a `.env` file based on `.env.example` with your `TELEGRAM_TOKEN` and `ALLOWED_CHAT_IDS` (comma-separated).
3. Run with Docker Compose:

```bash
docker-compose up -d
```

## Usage

Talk to your bot on Telegram:
- `/add <keywords> [min_price] [max_price] [distance_in_km]`
- Alternately, paste a Wallapop or Vinted URL directly to track it.
- `/list` to view your active searches.
- `/delete <id>` to remove a search.
