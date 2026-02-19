"""Weather service for fetching weather data from OpenWeatherMap API."""
import datetime
import logging
import re
from collections import Counter, defaultdict
from typing import Optional

import pytz
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from pyowm.weatherapi30.forecaster import Forecaster
from pyowm.weatherapi30.observation import Observation
from timezonefinder import TimezoneFinder

from config import FORECAST_INTERVAL, LOCALE
from services.weather_formatter import WeatherFormatter
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
    """Service for weather data operations using OpenWeatherMap API."""

    def __init__(self, api_key: str) -> None:
        """Initialize weather service with API key."""
        config = get_default_config()
        config['language'] = LOCALE
        self.owm = OWM(api_key, config)
        self.mgr = self.owm.weather_manager()
        self.geo_mgr = self.owm.geocoding_manager()
        self.tz_finder = TimezoneFinder()
        self.formatter = WeatherFormatter()

    @staticmethod
    def icon_handler(icon: str) -> str:
        """Convert weather icon code to emoji."""
        if '01' not in icon:
            icon = re.sub(r'\D', '', icon)
        return _ICON_MAP.get(icon, '')

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
    ) -> Optional[Observation]:
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
    ) -> Optional[Forecaster]:
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

    def format_current_weather(self, username: str, data: dict) -> str:
        """Format current weather data as message. Delegates to WeatherFormatter."""
        return self.formatter.format_current_weather(username, data)

    def format_forecast(self, username: str, data: dict) -> str:
        """Format forecast data as message. Delegates to WeatherFormatter."""
        return self.formatter.format_forecast(username, data)
