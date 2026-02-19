"""Weather service for fetching and formatting weather data."""
import re
import datetime
import pytz
from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
from timezonefinder import TimezoneFinder
from collections import defaultdict, Counter
from typing import Optional
import logging
from config import DEGREE_SIGN, LOCALE, FORECAST_INTERVAL
from utils.bot_helpers import format_localized_weekday

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather operations using OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        """Initialize weather service with API key."""
        config = get_default_config()
        config['language'] = LOCALE
        self.owm = OWM(api_key, config)
        self.mgr = self.owm.weather_manager()
        self.geo_mgr = self.owm.geocoding_manager()
        self.tz_finder = TimezoneFinder()
    
    def is_online(self) -> bool:
        """Check if OWM API is online."""
        try:
            self.mgr.weather_at_place('London,GB')
            return True
        except Exception:
            return False
    
    @staticmethod
    def icon_handler(icon: str) -> str:
        """Convert weather icon code to emoji."""
        if '01' not in icon:
            icon = re.sub(r'\D', '', icon)
        icons = {
            '01d': '\U00002600', '01n': '\U0001F311', '02': '\U000026C5',
            '03': '\U00002601', '04': '\U00002601', '09': '\U00002614',
            '10': '\U00002614', '11': '\U000026A1', '13': '\U00002744',
            '50': '\U0001F32B'
        }
        return icons.get(icon, '')
    
    def _get_geo_info(self, lat: float, lon: float) -> dict:
        """Get country code and state via reverse geocoding API."""
        try:
            _, json_data = self.geo_mgr.http_client.get_json(
                'reverse', params={'lat': lat, 'lon': lon, 'limit': 1}
            )
            if json_data:
                return {
                    'country': json_data[0].get('country', ''),
                    'state': json_data[0].get('state', '')
                }
        except Exception as e:
            logger.error(f'Error fetching geo info: {e}')
        return {'country': '', 'state': ''}
    
    def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Optional[dict]:

        try:
            if lat is not None and lon is not None:
                observation = self.mgr.weather_at_coords(lat, lon)
            elif city:
                observation = self.mgr.weather_at_place(city)
            else:
                return None

            location = observation.location
            weather = observation.weather

            timezone_str = self.tz_finder.timezone_at(
                lng=location.lon, lat=location.lat
            )

            timezone = pytz.timezone(timezone_str) if timezone_str else pytz.utc
            timezone_str = timezone_str or 'UTC'

            utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            local_time = utc_now.astimezone(timezone)

            day = local_time.date()
            formatted_date = format_localized_weekday(day, LOCALE)

            geo_info = self._get_geo_info(location.lat, location.lon)

            return {
                'location_name': location.name,
                'country': geo_info['country'],
                'state': geo_info['state'],
                'icon': self.icon_handler(weather.weather_icon_name),
                'status': weather.detailed_status,
                'temp': round(weather.temperature('celsius')['temp']),
                'pressure': round(weather.barometric_pressure()['press'] * 0.75),
                'humidity': weather.humidity,
                'wind_speed': round(weather.wind()['speed']),
                'timezone': timezone_str,
                'date': formatted_date.capitalize(),
                'time': local_time.strftime('%H:%M:%S')
            }

        except Exception as e:
            logger.error(f'Error fetching current weather: {e}')
            return None
    
    def get_forecast(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Optional[dict]:

        try:
            if lat is not None and lon is not None:
                forecaster = self.mgr.forecast_at_coords(lat, lon, FORECAST_INTERVAL)
            elif city:
                forecaster = self.mgr.forecast_at_place(city, FORECAST_INTERVAL)
            else:
                return None

            if forecaster is None:
                return None

            fc = forecaster.forecast
            location = fc.location

            timezone_str = self.tz_finder.timezone_at(
                lng=location.lon, lat=location.lat
            )

            timezone = pytz.timezone(timezone_str) if timezone_str else pytz.utc
            timezone_str = timezone_str or 'UTC'

            geo_info = self._get_geo_info(location.lat, location.lon)

            daily_data = defaultdict(list)

            for weather_obj in fc:
                dt_local = datetime.datetime.fromtimestamp(
                    weather_obj.reference_time(),
                    tz=timezone
                )

                day = dt_local.date()

                daily_data[day].append({
                    'temp': weather_obj.temperature('celsius')['temp'],
                    'humidity': weather_obj.humidity,
                    'pressure': weather_obj.barometric_pressure()['press'] * 0.75,
                    'wind_speed': weather_obj.wind()['speed'],
                    'status': weather_obj.detailed_status,
                    'icon': self.icon_handler(weather_obj.weather_icon_name)
                })

            forecasts = []

            for day, entries in sorted(daily_data.items()):
                formatted_date = format_localized_weekday(day, LOCALE)

                temps = [e['temp'] for e in entries]
                humidity = [e['humidity'] for e in entries]
                pressure = [e['pressure'] for e in entries]
                wind_speed = [e['wind_speed'] for e in entries]

                statuses = [e['status'] for e in entries]
                icons = [e['icon'] for e in entries]

                forecasts.append({
                    'date': formatted_date.capitalize(),
                    'temp_min': round(min(temps)),
                    'temp_max': round(max(temps)),
                    'humidity_avg': round(sum(humidity) / len(humidity)),
                    'pressure_avg': round(sum(pressure) / len(pressure)),
                    'wind_speed_avg': round(sum(wind_speed) / len(wind_speed)),
                    'status': Counter(statuses).most_common(1)[0][0],
                    'icon': Counter(icons).most_common(1)[0][0]
                })

            return {
                'location_name': location.name,
                'country': geo_info['country'],
                'state': geo_info['state'],
                'timezone': timezone_str,
                'forecasts': forecasts
            }

        except Exception as e:
            logger.error(f'Error fetching forecast: {e}')
            return None
    
    @staticmethod
    def _country_flag(country_code: str) -> str:
        """Convert country code (e.g. 'UA') to flag emoji."""
        return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in country_code.upper())

    @staticmethod
    def format_current_weather(username: str, weather_data: dict) -> str:
        """Format current weather data as message."""
        answer = f"{username}, в <b>{weather_data['location_name']}</b>\n\n"
        if weather_data.get('state'):
            answer += f"\U0001F3F7 <i>Область:</i> <b>{weather_data['state']}</b>\n"
        if weather_data.get('country'):
            flag = WeatherService._country_flag(weather_data['country'])
            answer += f"{flag} <i>Страна:</i> <b>{weather_data['country']}</b>\n"
        answer += f"\U0001F30D <i>Часовой пояс:</i> <b>{weather_data['timezone']}</b>\n"
        answer += f"\U0001F4C5 <i>Дата:</i> <b>{weather_data['date']}</b>\n"
        answer += f"\U000023F0 <i>Текущее время:</i> <b>{weather_data['time']}</b>\n"
        answer += f"{weather_data['icon']} <i>Статус:</i> <b>{weather_data['status'].capitalize()}</b>\n"
        answer += f"\U0001F321 <i>Температура воздуха:</i> <b>{weather_data['temp']} {DEGREE_SIGN}C</b>\n"
        answer += f"\U0001F4CF <i>Давление:</i> <b>{weather_data['pressure']} мм</b>\n"
        answer += f"\U0001F4A7 <i>Влажность:</i> <b>{weather_data['humidity']} %</b>\n"
        answer += f"\U0001F4A8 <i>Скорость ветра:</i> <b>{weather_data['wind_speed']} м/c</b>\n\n"
        
        return answer
    
    @staticmethod
    def format_forecast(username: str, forecast_data: dict) -> str:
        """Format forecast data as message."""
        answer = f"{username}, в <b>{forecast_data['location_name']}</b>\n\n"
        if forecast_data.get('state'):
            answer += f"\U0001F3F7 <i>Область:</i> <b>{forecast_data['state']}</b>\n"
        if forecast_data.get('country'):
            flag = WeatherService._country_flag(forecast_data['country'])
            answer += f"{flag} <i>Страна:</i> <b>{forecast_data['country']}</b>\n"
        answer += f"\U0001F30D <i>Часовой пояс:</i> <b>{forecast_data['timezone']}</b>\n\n"

        for day in forecast_data['forecasts']:
            if day['temp_min'] == day['temp_max']:
                temp_label = 'Средняя температура воздуха'
                temp_str = day['temp_min']
            else:
                temp_label = 'Температура воздуха'
                temp_str = f"{day['temp_min']}...{day['temp_max']}"

            answer += f"\U0001F4C5 <i>Дата:</i> <b>{day['date']}</b>\n"
            answer += f"{day['icon']} <i>Статус:</i> <b>{day['status'].capitalize()}</b>\n"
            answer += f"\U0001F321 <i>{temp_label}:</i> <b>{temp_str} {DEGREE_SIGN}C</b>\n"
            answer += f"\U0001F4CF <i>Давление:</i> <b>{day['pressure_avg']} мм</b>\n"
            answer += f"\U0001F4A7 <i>Влажность:</i> <b>{day['humidity_avg']} %</b>\n"
            answer += f"\U0001F4A8 <i>Скорость ветра:</i> <b>{day['wind_speed_avg']} м/c</b>\n\n"

        return answer
