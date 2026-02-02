# Architecture Diagram

## Data Flow

```
Telegram Server
      ↓
   Webhook (HTTPS)
      ↓
   src/bot.py (aiohttp handler)
      ↓
   telebot.process_new_updates()
      ↓
   ┌─────────────────────────────────┐
   │  Handler Registration (bot.py)  │
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
src/bot.py
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
│                     src/bot.py                          │
│  - Initializes bot, services, handlers                  │
│  - Registers message handlers                           │
│  - Starts aiohttp server                                │
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
2. Telegram → Webhook → src/bot.py → handle_webhook()
3. src/bot.py → weather_message() → MessageHandlers.handle_weather_request()
4. MessageHandlers → WeatherService.get_current_weather(city="London")
5. WeatherService → OpenWeatherMap API
6. WeatherService → format_current_weather()
7. MessageHandlers → bot_helpers.reply_to_message()
8. bot_helpers → send_with_retry() → bot.reply_to()
9. Response sent to user
```

### Example 2: User clicks /start

```
1. User: "/start"
2. Telegram → Webhook → src/bot.py → handle_webhook()
3. src/bot.py → start_command() → CommandHandlers.handle_start()
4. CommandHandlers → bot_helpers.create_inline_keyboard()
5. CommandHandlers → bot_helpers.send_message()
6. bot_helpers → send_with_retry() → bot.send_message()
7. CommandHandlers → bot_helpers.send_sticker()
8. Response sent to user
```

### Example 3: User clicks inline button

```
1. User: clicks "forecast" button
2. Telegram → Webhook → src/bot.py → handle_webhook()
3. src/bot.py → callback_query() → CallbackHandlers.handle_callback()
4. CallbackHandlers → _handle_forecast_callback()
5. CallbackHandlers → bot_helpers.create_location_keyboard()
6. CallbackHandlers → bot_helpers.send_message()
7. CallbackHandlers → bot.register_next_step_handler()
8. Response sent to user
9. Next message from user → CommandHandlers.handle_forecast_input()
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
get_env_or_exit("OWM_KEY")
     ↓
get_env_or_exit("TELEBOT_KEY")
     ↓
get_webhook_host() → Try IP services
     ↓
find_ssl_files() → Scan directory
     ↓
All config loaded
     ↓
src/bot.py imports config
     ↓
Initialize services with config
     ↓
Start bot
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
