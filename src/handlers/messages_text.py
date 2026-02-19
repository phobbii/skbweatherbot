"""Message text constants for bot responses."""
from typing import Sequence

# Author information
AUTHOR_INFO = (
    "\U0001F537 Автор: <b>Yevhen Skyba</b>\n"
    "\U0001F537 Email: skiba.eugene@gmail.com\n"
    "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
    "\U0001F537 Telegram: @phobbii"
)

# Instruction fragments
INSTRUCTION_LOCATION = "\U0001F537 Узнать погоду по геолокации - /location.\n"
INSTRUCTION_FORECAST = "\U0001F537 Прогноз на 5 дней - /forecast.\n"
INSTRUCTION_HELP = "\U0001F537 Справка - /help.\n"
INSTRUCTION_AUTHOR = "\U0001F537 Об авторе - /author.\n"

INSTRUCTION_LOCATION_BUTTON = "\U0001F537 Узнать погоду по геолокации - \U0001F310 location.\n"
INSTRUCTION_HELP_BUTTON = "\U0001F537 Справка - help.\n"
INSTRUCTION_AUTHOR_BUTTON = "\U0001F537 Об авторе - author.\n"

# Message templates
MSG_ENTER_CITY_LATIN = "{username}, введите город, чтобы узнать погоду.\n"
MSG_EXAMPLE_CITY = "\U0001F537 Пример: <b>Kharkiv</b>.\n"
MSG_CITY_NOT_FOUND = "<b>{city}</b> не найден.\n"
MSG_PRESS_LOCATION_BUTTON = "{username}, нажмите \U0001F310 location, чтобы отправить геолокацию.\n"
MSG_ENTER_CITY_OR_LOCATION = (
    "{username}, для получения прогноза на 5 дней, введите город или\n"
    "нажмите \U0001F310 location, чтобы отправить геолокацию.\n"
)
MSG_SERVICE_UNAVAILABLE = (
    "{username}, извините, сервис погоды сейчас недоступен.\n"
    "Попробуйте снова немного позже.\n"
)


def get_start_message(username: str) -> str:
    """Get start command message."""
    return (
        f"Здравствуйте, {username}!\n"
        "Чтобы узнать погоду, введите город или отправьте геолокацию - /location.\n"
        f"{INSTRUCTION_FORECAST}"
        f"{INSTRUCTION_HELP}"
        f"{INSTRUCTION_AUTHOR}"
    )


def get_help_message(username: str) -> str:
    """Get help message."""
    return (
        f"{MSG_ENTER_CITY_LATIN.format(username=username)}"
        f"{MSG_EXAMPLE_CITY}"
        f"{INSTRUCTION_LOCATION}"
        f"{INSTRUCTION_FORECAST}"
        f"{INSTRUCTION_AUTHOR}"
    )


def get_city_not_found_message(city: str, instructions: Sequence[str] = ()) -> str:
    """Get city not found message with configurable instructions."""
    if not instructions:
        instructions = (INSTRUCTION_LOCATION, INSTRUCTION_FORECAST, INSTRUCTION_HELP)
    return MSG_CITY_NOT_FOUND.format(city=city) + "".join(instructions)


def get_forecast_help_message(username: str) -> str:
    """Get forecast help message."""
    return (
        f"{MSG_ENTER_CITY_LATIN.format(username=username)}"
        f"{MSG_EXAMPLE_CITY}"
        f"{INSTRUCTION_LOCATION_BUTTON}"
        f"{INSTRUCTION_AUTHOR_BUTTON}"
    )
