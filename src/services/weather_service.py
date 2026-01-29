"""Weather service for fetching and formatting weather data."""
import re
import datetime
import pytz
import pyowm
from tzwhere import tzwhere
from typing import Optional
import logging
from config import DEGREE_SIGN

logger = logging.getLogger(__name__)


class WeatherService:
    """Service for weather operations using OpenWeatherMap API."""
    
    def __init__(self, api_key: str):
        """Initialize weather service with API key."""
        self.owm = pyowm.OWM(API_key=api_key, language="ru")
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
    
    def get_current_weather(self, city: Optional[str] = None, 
                           lat: Optional[float] = None, 
                           lon: Optional[float] = None) -> Optional[dict]:
        """Get current weather by city name or coordinates."""
        try:
            if lat is not None and lon is not None:
                observation = self.owm.weather_at_coords(lat, lon)
            elif city:
                observation = self.owm.weather_at_place(city)
            else:
                return None
            
            location = observation.get_location()
            weather = observation.get_weather()
            timezone_str = self.tz_finder.tzNameAt(location.get_lat(), location.get_lon())
            
            result = {
                'location_name': location.get_name(),
                'icon': self.icon_handler(weather.get_weather_icon_name()),
                'status': weather.get_detailed_status(),
                'temp': int(weather.get_temperature('celsius')["temp"]),
                'pressure': int(float(weather.get_pressure()['press']) * 0.75),
                'humidity': weather.get_humidity(),
                'wind_speed': weather.get_wind()['speed'],
                'timezone': timezone_str
            }
            
            if timezone_str:
                timezone = pytz.timezone(timezone_str)
                dt = datetime.datetime.utcnow()
                current_time = dt + timezone.utcoffset(dt)
                result['date'] = str(current_time).split()[0]
                result['time'] = str(current_time).split()[-1].split('.')[0]
            
            return result
        except Exception as e:
            logger.error(f"Error fetching current weather: {e}")
            return None
    
    def get_forecast(self, city: Optional[str] = None,
                    lat: Optional[float] = None,
                    lon: Optional[float] = None) -> Optional[dict]:
        """Get 3-day weather forecast."""
        try:
            if lat is not None and lon is not None:
                forecast = self.owm.three_hours_forecast_at_coords(lat, lon)
            elif city:
                forecast = self.owm.three_hours_forecast(city)
            else:
                return None
            
            location = forecast.get_forecast().get_location()
            timezone_str = self.tz_finder.tzNameAt(location.get_lat(), location.get_lon())
            
            if not timezone_str:
                return None
            
            timezone = pytz.timezone(timezone_str)
            dt = datetime.datetime.utcnow()
            current_time = dt + timezone.utcoffset(dt)
            
            forecasts = []
            for i in range(1, 4):
                timer = current_time + datetime.timedelta(days=i)
                forecast_weather = forecast.get_weather_at(timer)
                
                forecasts.append({
                    'date': str(timer).split()[0],
                    'icon': self.icon_handler(forecast_weather.get_weather_icon_name()),
                    'status': forecast_weather.get_detailed_status(),
                    'temp': int(forecast_weather.get_temperature('celsius')["temp"]),
                    'pressure': int(float(forecast_weather.get_pressure()['press']) * 0.75),
                    'humidity': forecast_weather.get_humidity(),
                    'wind_speed': int(forecast_weather.get_wind()['speed'])
                })
            
            return {
                'location_name': location.get_name(),
                'timezone': timezone_str,
                'forecasts': forecasts
            }
        except Exception as e:
            logger.error(f"Error fetching forecast: {e}")
            return None
    
    @staticmethod
    def format_current_weather(username: str, weather_data: dict) -> str:
        """Format current weather data as message."""
        answer = f"{username}, в <b>{weather_data['location_name']}</b>\n\n"
        
        if 'timezone' in weather_data and weather_data['timezone']:
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
            answer += f"\U0001F539 <i>Дата:</i>\U0001F4C6 <b>{day['date']}</b>\n"
            answer += f"\U0001F539 <i>Статус:</i> {day['icon']} <b>{day['status'].capitalize()}</b>\n"
            answer += f"\U0001F539 <i>Температура воздуха:</i> \U0001F321 <b>{day['temp']} {DEGREE_SIGN}C</b>\n"
            answer += f"\U0001F539 <i>Давление:</i> <b>{day['pressure']} мм</b>\n"
            answer += f"\U0001F539 <i>Влажность:</i> <b>{day['humidity']} %</b>\n"
            answer += f"\U0001F539 <i>Скорость ветра:</i> <b>{day['wind_speed']} м/c</b>\n\n"
        
        return answer
