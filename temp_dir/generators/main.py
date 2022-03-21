import re
from pytz import timezone
from datetime import datetime

class Answers(object):

    def __init__(self) -> None:
        self.degree_sign = u'\N{DEGREE SIGN}' 

    def welcome_help(self, username, location_cmd, forecast_cmd, help_cmd, author_cmd, city_name=None):
        if city_name:
            answer = f'{username}, введите название города латиницей.\n'
            answer += f'\U0001F537 Пример: <b>{city_name}</b>.\n'
            answer += f'\U0001F537 Прогноз погоды по местоположению - /{location_cmd}.\n'
        else:
            answer = f'Привет {username}.\n'
            answer += f'\U0001F537 Введите город латиницей для получения погоды или\n'
            answer += f'отправьте текущее местоположение - /{location_cmd}.\n'
        answer += f'\U0001F537 Прогноз на 3 дня - /{forecast_cmd}.\n'
        answer += f'\U0001F537 Помощь - /{help_cmd}.\n'
        answer += f'\U0001F537 Информации об авторе - /{author_cmd}.\n'

    def author(self, name, email, linkedin_url, tg_alias):
        answer = f'\U0001F537 Author: <b>{name}</b>\n'
        answer += f'\U0001F537 Email: {email}\n'
        answer += f'\U0001F537 LinkedIn: {linkedin_url}\n'
        answer += f'\U0001F537 Telegram: {tg_alias}'
        return answer

    def geo(self, username, button_name):
        answer = f'{username}, нажмите на кнопку "\U0001F310 {button_name}" для отправки местоположения\n'
        return answer

    def forecast(self, username, button_name):
        answer = f'{username}, введите город для получения прогноза на 3 дня или\n'
        answer += f'нажмите "\U0001F310 {button_name}" для отправки местоположения\n'
        return answer

    def errors(self, username, location_cmd, forecast_cmd, help_cmd, city_name=None):
        if city_name:
            answer = f'<b>{city_name}</b> не найден!\n'
        else:
            answer = f'{username}, пожалуйста введите название города латиницей.\n'
        answer += f'\U0001F537 Прогноз погоды по местоположению - /{location_cmd}.\n'
        answer += f'\U0001F537 Прогноз на 3 дня - /{forecast_cmd}.\n'
        answer += f'\U0001F537 Помощь - /{help_cmd}.\n'
        return answer

    def forecast_errors(self, username=None, city_name=None):
        if username is not None and city_name is None:
            answer = f'{username.title()}, пожалуйста введите название города латиницей.\n'
        elif username is None and city_name is not None:
            answer = f'<b>{str(city_name).capitalize()}</b> не найден!\n'
        answer += '\U0001F537 Прогноз погоды по местоположению - "\U0001F310 location".\n'
        answer += '\U0001F537 Помощь - help.\n'
        return answer

    def forecast_help(self, username, city_name):
        answer = f'{username.title()}, введите название города латиницей.\n'
        answer += f'\U0001F537 Пример: <b>{city_name}</b>.\n'
        answer += '\U0001F537 Прогноз погоды по местоположению - "\U0001F310 location".\n'
        answer += '\U0001F537 Информации об авторе - author.\n'
        return answer

    def weather(self, username, location_name, icon, detailed_status, temp, pressure, humidity, wind_speed, tzone=None):
        answer = f'{username.title()}, в <b>{location_name}</b>\n\n'
        if tzone:
            tz = timezone(timezone)
            current_time = datetime.utcnow() + tz.utcoffset(datetime.utcnow())
            answer += f'\U0001F539 <i>Часовой пояс:</i> <b>{tzone}</b>\n'
            answer += f'\U0001F539 <i>Дата:</i> \U0001F4C6 <b>{str(current_time).split()[0]}</b>\n'
            answer += f'\U0001F539 <i>Текущее время:</i> \U0000231A <b>{str(current_time).split()[-1].split(".")[0]}</b>\n'
        answer += f'\U0001F539 <i>Статус:</i> {icon} <b>{detailed_status}</b>\n'
        answer += f'\U0001F539 <i>Температура воздуха:</i> \U0001F321 <b>{temp} {self.degree_sign}C</b>\n'
        answer += f'\U0001F539 <i>Давление:</i> <b>{pressure} мм</b>\n'
        answer += f'\U0001F539 <i>Влажность:</i> <b>{humidity} %</b>\n'
        answer += f'\U0001F539 <i>Скорость ветра:</i> <b>{wind_speed} м/c</b>\n\n'
        return answer

    def forecast_weather(self, username=None, location_name=None, tzone=None, date=None, icon=None, 
                         detailed_status=None, temp=None, pressure=None, humidity=None, wind_speed=None):
        if username:
            answer = f'{username.title()}, в <b>{location_name}</b>\n'
            answer += f'\U0001F539 <i>Часовой пояс:</i> <b>{tzone}</b>\n\n'
        else:
            answer = f'\U0001F539 <i>Дата:</i>\U0001F4C6 <b>{date}</b>\n'
            answer += f'\U0001F539 <i>Статус:</i> {icon} <b>{detailed_status}</b>\n'
            answer += f'\U0001F539 <i>Температура воздуха:</i> \U0001F321 <b>{temp} {self.degree_sign}C</b>\n'
            answer += f'\U0001F539 <i>Давление:</i> <b>{pressure} мм</b>\n'
            answer += f'\U0001F539 <i>Влажность:</i> <b>{humidity} %</b>\n'
            answer += f'\U0001F539 <i>Скорость ветра:</i> <b>{wind_speed} м/c</b>\n\n'
        return answer

    def service_unavailable(self, username):
        answer = f'{username}, прошу прощения, в данный момент сервис погоды не доступен!\n'
        answer += 'Попробуйте позже\n'
        return answer