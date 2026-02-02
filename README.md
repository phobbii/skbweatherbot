# SKB Weather Bot

Telegram weather bot providing current weather and 5-day forecasts using OpenWeatherMap API.

Bot link: https://telegram.me/skbweatherbot

## Project Structure

```
/
├── Dockerfile                      # Docker build configuration
├── deploy_container.sh             # Automated deployment script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── DOCKER.md                       # Docker deployment guide
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
- Webhook-based deployment

## Requirements

**Note:** The bot requires a public static IP address for webhook functionality in both development and production environments.

### Development
- Python 3.9+
- Public static IP address
- SSL certificate and key files (.pem and .key) in the project directory
- Environment variables (see below)

### Production (Docker)
- Docker 17.05+
- Linux server with public static IP address
- Open HTTPS port (e.g., 8443)
- Root access for deployment

## Environment Variables

Set the following environment variables before running:

```bash
export OWM_KEY="your_openweathermap_api_key"
export TELEBOT_KEY="your_telegram_bot_token"
export WEBHOOK_PORT="listener_preferred_port"
export WEBHOOK_LISTEN="your_public_ip"
```

## Running the Bot

### For Development (Local)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (see above)

3. Generate SSL certificate files (.pem and .key)
```bash
cd src
openssl req -newkey rsa:2048 -sha256 -nodes \
    -keyout ${BOT_HOME}/url_private.key \
    -x509 -days 3650 \
    -out ${BOT_HOME}/url_certificate.pem \
    -subj "/C=US/ST=State/O=Organization/CN=${WEBHOOK_HOST}" \
    && curl -s -F "url=https://${WEBHOOK_HOST}:${WEBHOOK_PORT}" \
    -F "certificate=@url_certificate.pem" \
    https://api.telegram.org/bot${TELEBOT_KEY}/setWebhook
```

4. Run the bot:
```bash
python3 bot.py
```

The bot will:
1. Detect your public IP address for webhook setup
2. Start an aiohttp server with SSL
3. Listen for incoming webhook requests

### For Production (Docker)

1. Ensure Docker is installed (version >= 17.05)
2. Run the deployment script:
```bash
./deploy_container.sh --owm YOUR_KEY --telegram YOUR_TOKEN --port 8443
```

The deployment script will:
1. Detect your public IP automatically
2. Build a Docker image with all dependencies
3. Generate SSL certificates
4. Configure the webhook
5. Start the container with auto-restart enabled

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
