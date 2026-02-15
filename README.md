# SKB Weather Bot

Telegram weather bot providing current weather and 5-day forecasts using OpenWeatherMap API.

Bot link: https://telegram.me/skbweatherbot

## Project Structure

```
/
├── gcp-cloudbuild.yaml             # GCP Cloud Build deployment config
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── ARCHITECTURE.md                 # Architecture documentation
└── src/                            # Source code
    ├── bot.py                      # Main entry point
    ├── config.py                   # Configuration and environment variables
    ├── handlers/                   # Message and command handlers
    │   ├── __init__.py
    │   ├── base.py                # Base handler with common functionality
    │   ├── shared.py              # Shared response handlers (help, author)
    │   ├── commands.py            # Command handlers (/start, /help, etc.)
    │   ├── messages.py            # Message handlers (weather requests)
    │   └── callbacks.py           # Inline button callback handlers
    ├── services/                   # Business logic
    │   ├── __init__.py
    │   └── weather_service.py     # Weather API integration
    └── utils/                      # Helper functions
        ├── __init__.py
        └── bot_helpers.py         # Bot utility functions (retry, keyboards, etc.)
```

## Features

- Current weather by city name or GPS location
- 5-day weather forecast
- Automatic timezone detection
- Inline keyboard navigation
- Retry mechanism for API calls
- Comprehensive error handling
- Serverless deployment on Google Cloud Functions

## Requirements

### Development
- Python 3.9+
- Environment variables (see below)

### Production (Google Cloud Functions)
- GCP project with Cloud Functions and Secret Manager enabled
- Cloud Build trigger configured
- Secrets stored in GCP Secret Manager

## Environment Variables

Set the following environment variables before running:

```bash
export OWM_KEY="your_openweathermap_api_key"
export TELEBOT_KEY="your_telegram_bot_token"
export WEBHOOK_TOKEN="your_webhook_secret_token"
```

## Running the Bot

### For Development (Local)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (see above)

3. Run the bot (long polling mode):
```bash
cd src
python3 bot.py
```

### For Production (Google Cloud Functions)

Deployment is automated via Cloud Build (`gcp-cloudbuild.yaml`). The pipeline:

1. Deploys the bot as a gen2 Cloud Function with HTTP trigger
2. Configures the Telegram webhook to point to the function URL
3. Secrets (`OWM_KEY`, `TELEBOT_KEY`, `WEBHOOK_TOKEN`) are pulled from GCP Secret Manager

Cloud Build substitution variables:

| Variable | Default |
|---|---|
| `_REGION` | `us-east1` |
| `_NAME` | `skbweatherbot` |
| `_RUNTIME` | `python310` |
| `_ENTRY_POINT` | `webhook_run` |
| `_SOURCE` | `./src/` |
| `_MEMORY` | `512MB` |
| `_MAX_INSTANCES` | `3` |
| `_CONCURRENCY` | `1` |

## Bot Commands

- `/start` - Welcome message and main menu
- `/location` - Request GPS location for weather
- `/forecast` - Get 5-day weather forecast
- `/help` - Usage instructions
- `/author` - Author information

## Architecture Highlights

### Modular Design
- **Separation of concerns**: handlers, services, utilities, and configuration are isolated
- **Single responsibility**: each module has a clear, focused purpose
- **Inheritance hierarchy**: base classes eliminate code duplication
- **Easy to extend**: add new commands or services without touching existing code

### Code Quality
- **Type hints**: all functions have type annotations
- **Docstrings**: comprehensive documentation
- **DRY principle**: shared functionality in base classes
- **Logging**: proper logging

### Error Handling
- **Retry mechanism**: automatic retry for failed API calls
- **Graceful degradation**: user-friendly error messages
- **Service availability checks**: validates API status before requests
