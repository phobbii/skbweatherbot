# Architecture Diagram

## Data Flow

```
Telegram Server
      ↓
   Webhook (HTTPS)
      ↓
   Google Cloud Functions (gen2)
      ↓
   src/main.py → webhook_run(request)
      ↓
   Validate method (POST) & secret token
      ↓
   telebot.process_new_updates()
      ↓
   ┌─────────────────────────────────┐
   │  Handler Registration (main.py) │
   └─────────────────────────────────┘
      ↓
   ┌──────────────┬──────────────┬──────────────┐
   ↓              ↓              ↓              ↓
Commands      Messages      Callbacks    Wrong Content
   ↓              ↓              ↓              ↓
src/handlers/ src/handlers/ src/handlers/ src/handlers/
commands.py   messages.py   callbacks.py  messages.py
   ↓              ↓              ↓              ↓
   └──────────────┴──────────────┴──────────────┘
                  ↓
         ┌────────┴────────┐
         ↓                 ↓
   src/services/      src/utils/
   weather_service.py bot_helpers.py
         ↓                 ↓
   ┌─────┴─────┐    ┌─────┴─────┐
   ↓           ↓    ↓           ↓
OpenWeatherMap  Retry Logic  Keyboards
   API          Send Messages  Formatting
```

## Module Dependencies

```
src/main.py
├── src/config.py (settings)
├── src/services/weather_service.py
│   ├── src/config.py
│   ├── src/services/weather_formatter.py
│   └── src/utils/bot_helpers.py
├── src/handlers/commands.py
│   ├── src/config.py (stickers)
│   ├── src/handlers/base.py
│   ├── src/handlers/messages_text.py
│   ├── src/services/weather_service.py
│   └── src/utils/bot_helpers.py
├── src/handlers/messages.py
│   ├── src/handlers/base.py
│   ├── src/config.py
│   ├── src/services/weather_service.py
│   └── src/utils/bot_helpers.py
└── src/handlers/callbacks.py
    ├── src/config.py (stickers)
    ├── src/handlers/base.py
    ├── src/handlers/messages_text.py
    └── src/utils/bot_helpers.py

src/handlers/messages_text.py
└── (no dependencies - pure text templates)

src/handlers/base.py
├── src/config.py (stickers + error stickers)
├── src/handlers/messages_text.py (text templates)
└── src/utils/bot_helpers.py

src/utils/bot_helpers.py
└── emoji, babel.dates (external libraries)

src/services/weather_formatter.py
├── src/config.py
└── (no other dependencies)

src/services/weather_service.py
├── src/config.py
├── src/services/weather_formatter.py
└── src/utils/bot_helpers.py

src/config.py
└── (no dependencies - pure configuration)
```

## Class Relationships

```
┌─────────────────────────────────────────────────────────┐
│                     src/main.py                         │
│  - Initializes bot, services, handlers                  │
│  - Registers message handlers                           │
│  - is_private_or_mentioned(): group chat filter          │
│  - webhook_run(): Cloud Functions entry point           │
│  - local_run(): long polling for development            │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐
│  WeatherService    │  │  CommandHandlers    │  │  MessageHandlers  │
├────────────────────┤  ├─────────────────────┤  ├───────────────────┤
│+ owm               │  │+ bot                │  │+ bot              │
│+ mgr               │  │+ weather            │  │+ weather          │
│+ geo_mgr           │  ├─────────────────────┤  ├───────────────────┤
│+ tz_finder         │  │+ handle_start()     │  │+ handle_weather   │
│+ formatter         │  │+ handle_location()  │  │  _request()       │
├────────────────────┤  │+ handle_forecast    │  │+ handle_wrong     │
│+ icon_handler()    │  │  _command()         │  │  _content()       │
│+ get_current       │  │+ handle_forecast    │  └───────────────────┘
│  _weather()        │  │  _input()           │          │
│+ get_forecast()    │  │+ handle_help()      │          │
│+ format_current    │  │+ handle_author()    │          │
│  _weather()        │  └─────────────────────┘          │
│+ format_forecast() │          │                        │
│- _get_geo_info()   │          ↓                        ↓
│- _resolve          │  ┌────────────────────┐  ┌───────────────────┐
│  _timezone()       │  │ CallbackHandlers   │  │    BaseHandler    │
│- _get_observation()│  ├────────────────────┤  ├───────────────────┤
│- _get_forecaster() │  │+ bot               │  │+ bot              │
└────────────────────┘  │+ command_handlers  │  ├───────────────────┤
                        ├────────────────────┤  │+ send_response()  │
┌────────────────────┐  │+ handle_callback() │  │+ send_service     │
│ WeatherFormatter   │  │- _DISPATCH (dict)  │  │  _unavailable()   │
├────────────────────┤  └────────────────────┘  │+ send_city        │
│+ format_current    │          ↑               │  _not_found()     │
│  _weather()        │          │               │+ send_help()      │
│+ format_forecast() │          └───────────────│+ send_author()    │
│- _format_location  │                          │+ get_username()   │
│  _header()         │                          └───────────────────┘
│- _country_flag()   │
└────────────────────┘
```

## Request Flow Examples

### Example 1: User sends city name

```
1. User: "Kyiv" (in DM) or "Kyiv @bot" / reply to bot (in group)
2. Telegram → Webhook → Cloud Function → webhook_run(request)
3. Validate POST method & X-Telegram-Bot-Api-Secret-Token
4. src/main.py → is_private_or_mentioned() filter
5. src/main.py → weather_message() → strip @mention → MessageHandlers.handle_weather_request()
6. MessageHandlers → WeatherService.get_current_weather(city="Kyiv")
7. WeatherService → OpenWeatherMap API
8. WeatherService → WeatherFormatter.format_current_weather()
9. MessageHandlers → bot_helpers.reply_to_message()
10. bot_helpers → send_with_retry() → bot.reply_to()
11. Response sent to user
```

### Example 2: User clicks /start

```
1. User: "/start"
2. Telegram → Webhook → Cloud Function → webhook_run(request)
3. Validate POST method & secret token
4. src/main.py → start_command() → CommandHandlers.handle_start()
5. CommandHandlers → bot_helpers.create_inline_keyboard()
6. CommandHandlers → bot_helpers.send_message()
7. bot_helpers → send_with_retry() → bot.send_message()
8. CommandHandlers → bot_helpers.send_sticker()
9. Response sent to user
```

### Example 3: User clicks inline button

```
1. User: clicks "forecast" button
2. Telegram → Webhook → Cloud Function → webhook_run(request)
3. Validate POST method & secret token
4. src/main.py → callback_query() → CallbackHandlers.handle_callback()
5. CallbackHandlers → _DISPATCH → _on_forecast()
6. CallbackHandlers → bot_helpers.create_location_keyboard()
7. CallbackHandlers → bot_helpers.send_message()
8. CallbackHandlers → bot.register_next_step_handler()
9. Response sent to user
10. Next message from user → CommandHandlers.handle_forecast_input()
```

## Error Handling Flow

```
Any API Call
     ↓
send_with_retry()
     ↓
Try API call
     ↓
  Success? ──Yes──→ Return result
     ↓
    No
     ↓
Log error
     ↓
Retry < max? ──Yes──→ Sleep → Try again
     ↓
    No
     ↓
Raise exception
     ↓
Handler catches
     ↓
Send error message to user
```

## Configuration Loading

```
Program Start
     ↓
Import src/config.py
     ↓
os.getenv("OWM_KEY")
     ↓
os.getenv("TELEBOT_KEY")
     ↓
os.getenv("WEBHOOK_TOKEN")
     ↓
os.getenv("BOT_USERNAME") (default: "skbweatherbot")
     ↓
All config loaded
     ↓
src/main.py imports config
     ↓
Initialize services with config
     ↓
Start bot (webhook_run or local_run)
```

## Deployment Flow

```
Cloud Build Trigger
     ↓
gcp-cloudbuild.yaml
     ↓
Step 1: DEPLOY
  gcloud functions deploy (gen2)
  - Set runtime, region, memory, env vars
  - Secrets from GCP Secret Manager
     ↓
Step 2: WEBHOOK
  - Get deployed function URL
  - Delete previous Telegram webhook
  - Set new webhook with secret token
     ↓
Bot live and receiving updates
```

## Key Design Patterns Used

1. **Separation of Concerns**: Each module has single responsibility
2. **Inheritance**: BaseHandler provides common functionality to all handlers
3. **Composition**: Message text templates reused across handlers
4. **Dependency Injection**: Services and handlers passed to constructors
5. **Factory Pattern**: Keyboard creation functions
6. **Retry Pattern**: Generic retry wrapper
7. **Formatter Pattern**: Dedicated WeatherFormatter class for message formatting
8. **Strategy Pattern**: Different handlers for different message types
9. **Facade Pattern**: bot_helpers simplifies complex operations
10. **Guard Pattern**: `is_private_or_mentioned()` filters messages in group chats
