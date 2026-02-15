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
   │  Handler Registration (main.py)  │
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
│   └── src/config.py
├── src/handlers/commands.py
│   ├── src/handlers/base.py
│   ├── src/handlers/shared.py
│   ├── src/services/weather_service.py
│   └── src/utils/bot_helpers.py
├── src/handlers/messages.py
│   ├── src/handlers/base.py
│   ├── src/services/weather_service.py
│   └── src/utils/bot_helpers.py
└── src/handlers/callbacks.py
    ├── src/handlers/base.py
    ├── src/handlers/shared.py
    └── src/utils/bot_helpers.py

src/handlers/shared.py
├── src/handlers/base.py
└── src/utils/bot_helpers.py

src/handlers/base.py
├── src/utils/bot_helpers.py
└── src/config.py

src/utils/bot_helpers.py
└── (no dependencies - pure utilities)

src/services/weather_service.py
└── src/config.py

src/config.py
└── (no dependencies - pure configuration)
```

## Class Relationships

```
┌─────────────────────────────────────────────────────────┐
│                     src/main.py                         │
│  - Initializes bot, services, handlers                  │
│  - Registers message handlers                           │
│  - webhook_run(): Cloud Functions entry point            │
│  - local_run(): long polling for development            │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│WeatherService│  │CommandHandlers│ │MessageHandlers│
├──────────────┤  ├──────────────┤  ├──────────────┤
│+ owm         │  │+ bot         │  │+ bot         │
│+ tz_finder   │  │+ weather     │  │+ weather     │
├──────────────┤  │+ shared      │  ├──────────────┤
│+ is_online() │  ├──────────────┤  │+ handle_     │
│+ get_current │  │+ handle_start│  │  weather_req │
│+ get_forecast│  │+ handle_help │  │+ handle_wrong│
│+ format_*()  │  │+ handle_     │  │  _content    │
└──────────────┘  │  forecast    │  └──────────────┘
                  └──────────────┘          │
                          │                 │
                          ↓                 ↓
                  ┌──────────────┐  ┌──────────────┐
                  │CallbackHandlers│ │  BaseHandler │
                  ├──────────────┤  ├──────────────┤
                  │+ bot         │  │+ bot         │
                  │+ cmd_handlers│  ├──────────────┤
                  │+ shared      │  │+ send_response│
                  ├──────────────┤  │+ send_service│
                  │+ handle_     │  │  _unavailable│
                  │  callback    │  │+ send_city_  │
                  └──────────────┘  │  not_found   │
                          ↑         │+ send_cyrillic│
                          │         │  _error      │
                          │         └──────────────┘
                          │                 ↑
                          └─────────────────┤
                                            │
                                    ┌──────────────┐
                                    │SharedResponses│
                                    ├──────────────┤
                                    │+ bot         │
                                    ├──────────────┤
                                    │+ send_help   │
                                    │+ send_author │
                                    └──────────────┘
```

## Request Flow Examples

### Example 1: User sends city name

```
1. User: "London"
2. Telegram → Webhook → Cloud Function → webhook_run(request)
3. Validate POST method & X-Telegram-Bot-Api-Secret-Token
4. src/main.py → weather_message() → MessageHandlers.handle_weather_request()
5. MessageHandlers → WeatherService.get_current_weather(city="London")
6. WeatherService → OpenWeatherMap API
7. WeatherService → format_current_weather()
8. MessageHandlers → bot_helpers.reply_to_message()
9. bot_helpers → send_with_retry() → bot.reply_to()
10. Response sent to user
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
5. CallbackHandlers → _handle_forecast_callback()
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
3. **Composition**: SharedResponses reused across command and callback handlers
4. **Dependency Injection**: Services and handlers passed to constructors
5. **Factory Pattern**: Keyboard creation functions
6. **Retry Pattern**: Generic retry wrapper
7. **Template Method**: Format methods in WeatherService
8. **Strategy Pattern**: Different handlers for different message types
9. **Facade Pattern**: bot_helpers simplifies complex operations
