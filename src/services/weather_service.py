"""Weather service for fetching and formatting weather data."""
import datetime
import logging
import re
from collections import Counter, defaultdict
from typing import Optional

import pytz
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from timezonefinder import TimezoneFinder

from config import DEGREE_SIGN, FORECAST_INTERVAL, LOCALE
from utils.bot_helpers import format_localized_weekday

logger = logging.getLogger(__name__)

# Weather icon code → emoji mapping
_ICON_MAP: dict[str, str] = {
    '01d': '\U00002600', '01n': '\U0001F311', '02': '\U000026C5',
    '03': '\U00002601', '04': '\U00002601', '09': '\U00002614',
    '10': '\U00002614', '11': '\U000026A1', '13': '\U00002744',
    '50': '\U0001F32B',
}

# Pressure conversion factor: hPa → mmHg
_HPA_TO_MMHG = 0.75


class WeatherService:
    """Service for weather operations using OpenWeatherMap API."""

    def __init__(self, api_key: str) -> None:
        """Initialize weather service with API key."""
        config = get_default_config()
        config['language'] = LOCALE
        self.owm = OWM(api_key, config)
        self.mgr = self.owm.weather_manager()
        self.geo_mgr = self.owm.geocoding_manager()
        self.tz_finder = TimezoneFinder()

    @staticmethod
    def icon_handler(icon: str) -> str:
        """Convert weather icon code to emoji."""
        if '01' not in icon:
            icon = re.sub(r'\D', '', icon)
        return _ICON_MAP.get(icon, '')

    @staticmethod
    def _country_flag(country_code: str) -> str:
        """Convert country code (e.g. 'UA') to flag emoji."""
        return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in country_code.upper())

    def is_online(self) -> bool:
        """Check if OWM API is online."""
        try:
            self.mgr.weather_at_place('London,GB')
            return True
        except Exception:
            return False

    def _get_geo_info(self, lat: float, lon: float) -> dict[str, str]:
        """Get country code and state via reverse geocoding API."""
        try:
            _, json_data = self.geo_mgr.http_client.get_json(
                'reverse', params={'lat': lat, 'lon': lon, 'limit': 1}
            )
            if json_data:
                return {
                    'country': json_data[0].get('country', ''),
                    'state': json_data[0].get('state', ''),
                }
        except Exception as e:
            logger.error(f'Error fetching geo info: {e}')
        return {'country': '', 'state': ''}

    def _resolve_timezone(self, lat: float, lon: float) -> tuple[pytz.BaseTzInfo, str]:
        """Resolve timezone for given coordinates."""
        tz_name = self.tz_finder.timezone_at(lng=lon, lat=lat)
        if tz_name:
            return pytz.timezone(tz_name), tz_name
        return pytz.utc, 'UTC'

    def _get_observation(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ):
        """Get weather observation by city or coordinates."""
        if lat is not None and lon is not None:
            return self.mgr.weather_at_coords(lat, lon)
        if city:
            return self.mgr.weather_at_place(city)
        return None

    def _get_forecaster(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ):
        """Get forecast by city or coordinates."""
        if lat is not None and lon is not None:
            return self.mgr.forecast_at_coords(lat, lon, FORECAST_INTERVAL)
        if city:
            return self.mgr.forecast_at_place(city, FORECAST_INTERVAL)
        return None

    def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> Optional[dict]:
        """Fetch current weather data for a city or coordinates."""
        try:
            observation = self._get_observation(city, lat, lon)
            if not observation:
                return None

            location = observation.location
            weather = observation.weather
            timezone, tz_name = self._resolve_timezone(location.lat, location.lon)

            utc_now = datetime.datetime.now(tz=pytz.utc)
            local_time = utc_now.astimezone(timezone)
            formatted_date = format_localized_weekday(local_time.date(), LOCALE)

            geo_info = self._get_geo_info(location.lat, location.lon)

            return {
                'location_name': location.name,
                'country': geo_info['country'],
                'state': geo_info['state'],
                'icon': self.icon_handler(weather.weather_icon_name),
                'status': weather.detailed_status,
                'temp': round(weather.temperature('celsius')['temp']),
                'pressure': round(weather.barometric_pressure()['press'] * _HPA_TO_MMHG),
                'humidity': weather.humidity,
                'wind_speed': round(weather.wind()['speed']),
                'timezone': tz_name,
                'date': formatted_date.capitalize(),
                'time': local_time.strftime('%H:%M:%S'),
            }
        except Exception as e:
            logger.error(f'Error fetching current weather: {e}')
            return None

    def get_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
    ) -> Optional[dict]:
        """Fetch 5-day forecast data for a city or coordinates."""
        try:
            forecaster = self._get_forecaster(city, lat, lon)
            if not forecaster:
                return None

            fc = forecaster.forecast
            location = fc.location
            timezone, tz_name = self._resolve_timezone(location.lat, location.lon)
            geo_info = self._get_geo_info(location.lat, location.lon)

            daily_data: defaultdict[datetime.date, list[dict]] = defaultdict(list)
            for weather_obj in fc:
                dt_local = datetime.datetime.fromtimestamp(
                    weather_obj.reference_time(), tz=timezone,
                )
                daily_data[dt_local.date()].append({
                    'temp': weather_obj.temperature('celsius')['temp'],
                    'humidity': weather_obj.humidity,
                    'pressure': weather_obj.barometric_pressure()['press'] * _HPA_TO_MMHG,
                    'wind_speed': weather_obj.wind()['speed'],
                    'status': weather_obj.detailed_status,
                    'icon': self.icon_handler(weather_obj.weather_icon_name),
                })

            forecasts = []
            for day, entries in sorted(daily_data.items()):
                formatted_date = format_localized_weekday(day, LOCALE)
                temps = [e['temp'] for e in entries]
                n = len(entries)
                forecasts.append({
                    'date': formatted_date.capitalize(),
                    'temp_min': round(min(temps)),
                    'temp_max': round(max(temps)),
                    'humidity_avg': round(sum(e['humidity'] for e in entries) / n),
                    'pressure_avg': round(sum(e['pressure'] for e in entries) / n),
                    'wind_speed_avg': round(sum(e['wind_speed'] for e in entries) / n),
                    'status': Counter(e['status'] for e in entries).most_common(1)[0][0],
                    'icon': Counter(e['icon'] for e in entries).most_common(1)[0][0],
                })

            return {
                'location_name': location.name,
                'country': geo_info['country'],
                'state': geo_info['state'],
                'timezone': tz_name,
                'forecasts': forecasts,
            }
        except Exception as e:
            logger.error(f'Error fetching forecast: {e}')
            return None

    def _format_location_header(self, username: str, data: dict, trailing_newline: bool = True) -> str:
        """Format the common location header for weather messages.

        Args:
            trailing_newline: If True, adds an extra blank line after the header.
        """
        lines = [f"{username}, в <b>{data['location_name']}</b>\n"]
        if data.get('state'):
            lines.append(f"\U0001F5FA <i>Регион:</i> <b>{data['state']}</b>")
        if data.get('country'):
            flag = self._country_flag(data['country'])
            lines.append(f"{flag} <i>Код страны:</i> <b>{data['country']}</b>")
        lines.append(f"\U0001F30D <i>Часовой пояс:</i> <b>{data['timezone']}</b>")
        result = '\n'.join(lines) + '\n'
        if trailing_newline:
            result += '\n'
        return result

    def format_current_weather(self, username: str, data: dict) -> str:
        """Format current weather data as message."""
        header = self._format_location_header(username, data, trailing_newline=False)
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

    def format_forecast(self, username: str, data: dict) -> str:
        """Format forecast data as message."""
        answer = self._format_location_header(username, data)
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
