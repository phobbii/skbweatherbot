"""Weather service for fetching and formatting weather data."""
import re
import datetime
import pytz
import pyowm
from tzwhere import tzwhere
from collections import defaultdict, Counter
from typing import Optional
import logging
from config import DEGREE_SIGN, LOCALE
from utils.bot_helpers import format_localized_weekday

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather operations using OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        """Initialize weather service with API key."""
        self.owm = pyowm.OWM(API_key=api_key, language='ru')
        self.tz_finder = tzwhere.tzwhere()
    
    def is_online(self) -> bool:
        """Check if OWM API is online."""
        return self.owm.is_API_online()
    
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
    
    def get_current_weather(
        self,
        city: Optional[str] = None,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> Optional[dict]:

        try:
            if lat is not None and lon is not None:
                observation = self.owm.weather_at_coords(lat, lon)
            elif city:
                observation = self.owm.weather_at_place(city)
            else:
                return None

            location = observation.get_location()
            weather = observation.get_weather()

            timezone_str = self.tz_finder.tzNameAt(
                location.get_lat(),
                location.get_lon()
            )

            timezone = pytz.timezone(timezone_str) if timezone_str else pytz.utc
            timezone_str = timezone_str or 'UTC'

            utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
            local_time = utc_now.astimezone(timezone)

            day = local_time.date()
            formatted_date = format_localized_weekday(day, LOCALE)

            return {
                'location_name': location.get_name(),
                'icon': self.icon_handler(weather.get_weather_icon_name()),
                'status': weather.get_detailed_status(),
                'temp': int(weather.get_temperature('celsius')['temp']),
                'pressure': int(float(weather.get_pressure()['press']) * 0.75),
                'humidity': weather.get_humidity(),
                'wind_speed': weather.get_wind()['speed'],
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
                forecast = self.owm.three_hours_forecast_at_coords(lat, lon)
            elif city:
                forecast = self.owm.three_hours_forecast(city)
            else:
                return None

            location = forecast.get_forecast().get_location()

            timezone_str = self.tz_finder.tzNameAt(
                location.get_lat(),
                location.get_lon()
            )

            timezone = pytz.timezone(timezone_str) if timezone_str else pytz.utc
            timezone_str = timezone_str or 'UTC'

            daily_data = defaultdict(list)

            for weather_obj in forecast.get_forecast():
                dt_local = datetime.datetime.fromtimestamp(
                    weather_obj.get_reference_time(),
                    tz=timezone
                )

                day = dt_local.date()

                daily_data[day].append({
                    'temp': weather_obj.get_temperature('celsius')['temp'],
                    'humidity': weather_obj.get_humidity(),
                    'pressure': float(weather_obj.get_pressure()['press']) * 0.75,
                    'wind_speed': weather_obj.get_wind()['speed'],
                    'status': weather_obj.get_detailed_status(),
                    'icon': self.icon_handler(
                        weather_obj.get_weather_icon_name()
                    )
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
                    'temp_min': int(min(temps)),
                    'temp_max': int(max(temps)),
                    'humidity_avg': int(sum(humidity) / len(humidity)),
                    'pressure_avg': int(sum(pressure) / len(pressure)),
                    'wind_speed_avg': int(sum(wind_speed) / len(wind_speed)),
                    'status': Counter(statuses).most_common(1)[0][0],
                    'icon': Counter(icons).most_common(1)[0][0]
                })

            return {
                'location_name': location.get_name(),
                'timezone': timezone_str,
                'forecasts': forecasts
            }

        except Exception as e:
            logger.error(f'Error fetching forecast: {e}')
            return None
    
    @staticmethod
    def format_current_weather(username: str, weather_data: dict) -> str:
        """Format current weather data as message."""
        answer = f"{username}, в <b>{weather_data['location_name']}</b>\n\n"
        answer += f"\U0001F539 <i>Часовой пояс:</i> <b>{weather_data['timezone']}</b>\n"
        answer += f"\U0001F539 <i>Дата:</i> \U0001F4C6 <b>{weather_data['date']}</b>\n"
        answer += f"\U0001F539 <i>Текущее время:</i> \U0000231A <b>{weather_data['time']}</b>\n"
        answer += f"\U0001F539 <i>Статус:</i> {weather_data['icon']} <b>{weather_data['status'].capitalize()}</b>\n"
        answer += f"\U0001F539 <i>Температура воздуха:</i> \U0001F321 <b>{weather_data['temp']} {DEGREE_SIGN}C</b>\n"
        answer += f"\U0001F539 <i>Давление:</i> <b>{weather_data['pressure']} мм</b>\n"
        answer += f"\U0001F539 <i>Влажность:</i> <b>{weather_data['humidity']} %</b>\n"
        answer += f"\U0001F539 <i>Скорость ветра:</i> <b>{weather_data['wind_speed']} м/c</b>\n\n"
        
        return answer
    
    @staticmethod
    def format_forecast(username: str, forecast_data: dict) -> str:
        """Format forecast data as message."""
        answer = f"{username}, в <b>{forecast_data['location_name']}</b>\n"
        answer += f"\U0001F539 <i>Часовой пояс:</i> <b>{forecast_data['timezone']}</b>\n\n"

        for day in forecast_data['forecasts']:
            if day['temp_min'] == day['temp_max']:
                temp_label = 'Средняя температура воздуха'
                temp_str = day['temp_min']
            else:
                temp_label = 'Температура воздуха'
                temp_str = f"{day['temp_min']}...{day['temp_max']}"

            answer += f"\U0001F539 <i>Дата:</i> \U0001F4C6 <b>{day['date']}</b>\n"
            answer += f"\U0001F539 <i>Статус:</i> {day['icon']} <b>{day['status'].capitalize()}</b>\n"
            answer += f"\U0001F539 <i>{temp_label}:</i> \U0001F321 <b>{temp_str} {DEGREE_SIGN}C</b>\n"
            answer += f"\U0001F539 <i>Давление:</i> <b>{day['pressure_avg']} мм</b>\n"
            answer += f"\U0001F539 <i>Влажность:</i> <b>{day['humidity_avg']} %</b>\n"
            answer += f"\U0001F539 <i>Скорость ветра:</i> <b>{day['wind_speed_avg']} м/c</b>\n\n"

        return answer
