import re
from pyowm import OWM
from tzwhere import tzwhere


class Weather(object):
    
    def __init__(self, api_key, language):
        self.owm = OWM(API_key=api_key, language=language)

    def __icon(icon):
        if '01' not in icon:
            icon = re.sub('\D', '', icon)
        icons = {'01d': '\U00002600', '01n': '\U0001F311', '02': '\U000026C5',
                '03': '\U00002601', '04': '\U00002601', '09': '\U00002614',
                '10': '\U00002614', '11': '\U000026A1', '13': '\U00002744',
                '50': '\U0001F32B'}
        return icons[icon]

    def get_data(self, message, forecast=False):
        try:
            if forecast:
                if message.location is not None:
                    data = self.owm.three_hours_forecast_at_coords(message.location.latitude, message.location.longitude)
                else:
                    data = self.owm.three_hours_forecast(message.text)
            else:
                if message.location is not None:
                    data = self.owm.weather_at_coords(message.location.latitude, message.location.longitude)
                else:
                    data = self.owm.weather_at_place(message.text)
            return data
        except Exception as error:
            print(f'Weather get weather data unsuccessful, unexpected error occurred: {error}')
            return False

    def is_online(self):
        try:
            if self.owm.is_API_online():
                return True
        except Exception as error:
            print(f'Weather is online unsuccessful, unexpected error occurred: {error}')
            return False

    def get_weather(self, data, timer=None):
        if timer:
            observation = data.get_weather_at(timer)
            location = data.get_forecast().get_location()
        else:
            observation = data.get_weather()
            location = data.get_location()
        tf = tzwhere.tzwhere()
        weather = dict(LocationName = location.get_name(),
                        TimeZone = tf.tzNameAt(location.get_lat(), location.get_lon()),
                        Icon = self.__icon(observation.get_weather_icon_name()),
                        DetailedStatus = observation.get_detailed_status(),
                        Temp = int(observation.get_temperature('celsius')['temp']),
                        Pressure = int(float(observation.get_pressure()['press']) * 0.75),
                        Humidity = observation.get_humidity(),
                        WindSpeed = int(observation.get_wind()['speed']))
        return weather