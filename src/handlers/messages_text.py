"""Message text constants for bot responses."""

# Sticker IDs
STICKER_HELP = 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA'
STICKER_AUTHOR = 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA'
STICKER_START = 'CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ'
STICKER_CITY_NOT_FOUND = 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA'
STICKER_CYRILLIC_ERROR = 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA'

# Author information
AUTHOR_INFO = (
    "\U0001F537 Author: <b>Yevhen Skyba</b>\n"
    "\U0001F537 Email: skiba.eugene@gmail.com\n"
    "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
    "\U0001F537 Telegram: @phobbii"
)

# Common instructions
INSTRUCTION_LOCATION = "\U0001F537 Прогноз по местоположению - /location.\n"
INSTRUCTION_FORECAST = "\U0001F537 Прогноз на 5 дней - /forecast.\n"
INSTRUCTION_HELP = "\U0001F537 Помощь - /help.\n"
INSTRUCTION_AUTHOR = "\U0001F537 Информации об авторе - /author.\n"

INSTRUCTION_LOCATION_BUTTON = "\U0001F537 Прогноз по местоположению - '\U0001F310 location'.\n"
INSTRUCTION_HELP_BUTTON = "\U0001F537 Помощь - help.\n"
INSTRUCTION_AUTHOR_BUTTON = "\U0001F537 Информации об авторе - author.\n"

# Message templates
MSG_ENTER_CITY_LATIN = "{username}, введите название города латиницей.\n"
MSG_EXAMPLE_CITY = "\U0001F537 Пример: <b>Kharkiv</b>.\n"
MSG_CITY_NOT_FOUND = "<b>{city}</b> не найден!\n"
MSG_PRESS_LOCATION_BUTTON = "{username}, нажмите на кнопку '\U0001F310 location' для отправки местоположения\n"
MSG_ENTER_CITY_OR_LOCATION = "{username}, введите город для получения прогноза на 5 дней или\nнажмите '\U0001F310 location' для отправки местоположения\n"
MSG_SERVICE_UNAVAILABLE = "{username}, прошу прощения, в данный момент сервис погоды не доступен!\nПопробуйте позже\n"

# Start message
def get_start_message(username: str) -> str:
    """Get start command message."""
    return (
        f"Привет {username}.\n"
        "\U0001F537 Введите город латиницей для получения погоды или\n"
        "отправьте текущее местоположение - /location.\n"
        f"{INSTRUCTION_FORECAST}"
        f"{INSTRUCTION_HELP}"
        f"{INSTRUCTION_AUTHOR}"
    )

# Help message
def get_help_message(username: str) -> str:
    """Get help message."""
    return (
        f"{MSG_ENTER_CITY_LATIN.format(username=username)}"
        f"{MSG_EXAMPLE_CITY}"
        f"{INSTRUCTION_LOCATION}"
        f"{INSTRUCTION_FORECAST}"
        f"{INSTRUCTION_AUTHOR}"
    )

# Cyrillic error message
def get_cyrillic_error_message(username: str) -> str:
    """Get Cyrillic input error message."""
    return (
        f"{username}, пожалуйста введите название города латиницей.\n"
        f"{INSTRUCTION_LOCATION}"
        f"{INSTRUCTION_FORECAST}"
        f"{INSTRUCTION_HELP}"
    )

# City not found message
def get_city_not_found_message(city: str) -> str:
    """Get city not found message."""
    return (
        f"{MSG_CITY_NOT_FOUND.format(city=city)}"
        f"{INSTRUCTION_LOCATION}"
        f"{INSTRUCTION_FORECAST}"
        f"{INSTRUCTION_HELP}"
    )

# Forecast help message
def get_forecast_help_message(username: str) -> str:
    """Get forecast help message."""
    return (
        f"{MSG_ENTER_CITY_LATIN.format(username=username)}"
        f"{MSG_EXAMPLE_CITY}"
        f"{INSTRUCTION_LOCATION_BUTTON}"
        f"{INSTRUCTION_AUTHOR_BUTTON}"
    )

# Forecast error messages
def get_forecast_cyrillic_error(username: str) -> str:
    """Get forecast Cyrillic error message."""
    return (
        f"{username}, пожалуйста введите название города латиницей.\n"
        f"{INSTRUCTION_LOCATION_BUTTON}"
        f"{INSTRUCTION_HELP_BUTTON}"
    )

def get_forecast_city_not_found(city: str) -> str:
    """Get forecast city not found message."""
    return (
        f"{MSG_CITY_NOT_FOUND.format(city=city)}"
        f"{INSTRUCTION_LOCATION_BUTTON}"
        f"{INSTRUCTION_HELP_BUTTON}"
    )
