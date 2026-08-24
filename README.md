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
  - **Strict Vinted Filtering**: Ignores sponsored/zombie items by reading internal high-resolution timestamps.
- **Asynchronous Queues**: The scraping loop is decoupled from Telegram notifications, ensuring lightning-fast scans even if Telegram rate limits are hit.
- **Inline Management**: Unfollow searches directly from the Telegram notification using inline buttons.

## Installation via Docker Hub (Recommended)

Findly is available as a pre-built Docker image at [`uniextra/findly`](https://hub.docker.com/r/uniextra/findly). You do not need to clone the repository to run it.

Simply create a `docker-compose.yml` file anywhere on your server:

```yaml
services:
  findly:
    image: uniextra/findly:latest
    container_name: findly
    init: true
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
```

Then run:
```bash
docker-compose up -d
```

*(To change the Web UI port, change the left-side number in `ports`, e.g., `"8080:8000"`).*

## Setup Instructions (Build from source)

If you prefer to build the image yourself or modify the code:

1. Clone this repository.
2. Run with Docker Compose (No `.env` file required!):

```bash
docker-compose up -d --build
```

## First Time Configuration

1. Navigate to the Web UI at `http://localhost:8000` (or your server's IP/custom port).
2. Go to the **Settings** tab.
3. Configure your **Telegram Bot Token** and **Allowed Chat IDs**.
4. Click **Save & Restart**. The bot will seamlessly reload with your new settings.

## Usage

**Via Web UI (Recommended)**:
Navigate to your dashboard to view statistics, add new tracking queries (using the non-linear sliders or URL pasting), trigger manual refreshes, and review the history of all seen items.

**Via Telegram**:
- `/start` to see the welcome message.
- `/add <keywords> [min_price] [max_price] [distance_in_km]`
- Paste a Wallapop or Vinted URL directly in the chat to track it.
- `/list` to view your active searches.
- `/delete <id>` to remove a search.
