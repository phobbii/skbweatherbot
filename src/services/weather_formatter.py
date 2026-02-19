"""Weather data formatting for bot messages."""
from config import DEGREE_SIGN


class WeatherFormatter:
    """Formats weather data dicts into HTML messages for Telegram."""

    @staticmethod
    def _country_flag(country_code: str) -> str:
        """Convert country code (e.g. 'UA') to flag emoji."""
        return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in country_code.upper())

    @classmethod
    def _format_location_header(cls, username: str, data: dict, trailing_newline: bool = True) -> str:
        """Format the common location header for weather messages."""
        lines = [f"{username}, в <b>{data['location_name']}</b>\n"]
        if data.get('state'):
            lines.append(f"\U0001F5FA <i>Регион:</i> <b>{data['state']}</b>")
        if data.get('country'):
            flag = cls._country_flag(data['country'])
            lines.append(f"{flag} <i>Код страны:</i> <b>{data['country']}</b>")
        lines.append(f"\U0001F30D <i>Часовой пояс:</i> <b>{data['timezone']}</b>")
        result = '\n'.join(lines) + '\n'
        if trailing_newline:
            result += '\n'
        return result

    @classmethod
    def format_current_weather(cls, username: str, data: dict) -> str:
        """Format current weather data as message."""
        header = cls._format_location_header(username, data, trailing_newline=False)
        return (
            f"{header}"
            f"\U0001F4C5 <i>Дата:</i> <b>{data['date']}</b>\n"
            f"\U000023F0 <i>Текущее время:</i> <b>{data['time']}</b>\n"
            f"{data['icon']} <i>Статус:</i> <b>{data['status'].capitalize()}</b>\n"
            f"\U0001F321 <i>Температура воздуха:</i> <b>{data['temp']} {DEGREE_SIGN}C</b>\n"
            f"\U0001F4CA <i>Давление:</i> <b>{data['pressure']} мм</b>\n"
            f"\U0001F4A7 <i>Влажность:</i> <b>{data['humidity']} %</b>\n"
            f"\U0001F4A8 <i>Скорость ветра:</i> <b>{data['wind_speed']} м/c</b>\n\n"
        )

    @classmethod
    def format_forecast(cls, username: str, data: dict) -> str:
        """Format forecast data as message."""
        answer = cls._format_location_header(username, data)
        for day in data['forecasts']:
            if day['temp_min'] == day['temp_max']:
                temp_label = 'Средняя температура воздуха'
                temp_str = str(day['temp_min'])
            else:
                temp_label = 'Температура воздуха'
                temp_str = f"{day['temp_min']}...{day['temp_max']}"

            answer += (
                f"\U0001F4C5 <i>Дата:</i> <b>{day['date']}</b>\n"
                f"{day['icon']} <i>Статус:</i> <b>{day['status'].capitalize()}</b>\n"
                f"\U0001F321 <i>{temp_label}:</i> <b>{temp_str} {DEGREE_SIGN}C</b>\n"
                f"\U0001F4CA <i>Давление:</i> <b>{day['pressure_avg']} мм</b>\n"
                f"\U0001F4A7 <i>Влажность:</i> <b>{day['humidity_avg']} %</b>\n"
                f"\U0001F4A8 <i>Скорость ветра:</i> <b>{day['wind_speed_avg']} м/c</b>\n\n"
            )
        return answer
