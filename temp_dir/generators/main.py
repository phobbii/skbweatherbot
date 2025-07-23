class Answers(object):

    def __init__(self, author_name, author_email, author_linkedin, author_tg, 
                location_cmd, forecast_cmd, help_cmd, author_cmd):
        self.degree_sign = u'\N{DEGREE SIGN}'
        self.author_name = author_name
        self.author_email = author_email
        self.author_linkedin = author_linkedin
        self.author_tg = author_tg
        self.location_cmd = location_cmd
        self.forecast_cmd = forecast_cmd
        self.help_cmd = help_cmd
        self.author_cmd = author_cmd

    def welcome_help(self, username, city_name=None):
        if city_name:
            answer = f'{username}, введите название города латиницей.\n'
            answer += f'\U0001F537 Пример: <b>{city_name}</b>.\n'
            answer += f'\U0001F537 Прогноз погоды по местоположению - /{self.location_cmd}.\n'
        else:
            answer = f'Привет {username}.\n'
            answer += f'\U0001F537 Введите город латиницей для получения погоды или\n'
            answer += f'отправьте текущее местоположение - /{self.location_cmd}.\n'
        answer += f'\U0001F537 Прогноз на 3 дня - /{self.forecast_cmd}.\n'
        answer += f'\U0001F537 Помощь - /{self.help_cmd}.\n'
        answer += f'\U0001F537 Информации об авторе - /{self.author_cmd}.\n'
        return answer

    def author(self):
        answer = f'\U0001F537 Author: <b>{self.author_name}</b>\n'
        answer += f'\U0001F537 Email: {self.author_email}\n'
        answer += f'\U0001F537 LinkedIn: {self.author_linkedin}\n'
        answer += f'\U0001F537 Telegram: {self.author_tg}'
        return answer

    def geo(self, username):
        answer = f'{username}, нажмите на кнопку "\U0001F310 {self.location_cmd}" для отправки местоположения\n'
        return answer

    def forecast(self, username):
        answer = f'{username}, введите город для получения прогноза на 3 дня или\n'
        answer += f'нажмите "\U0001F310 {self.forecast_cmd}" для отправки местоположения\n'
        return answer

    def errors(self, username, city_name=None):
        if city_name:
            answer = f'<b>{city_name}</b> не найден!\n'
        else:
            answer = f'{username}, пожалуйста введите название города латиницей.\n'
        answer += f'\U0001F537 Прогноз погоды по местоположению - /{self.location_cmd}.\n'
        answer += f'\U0001F537 Прогноз на 3 дня - /{self.forecast_cmd}.\n'
        answer += f'\U0001F537 Помощь - /{self.help_cmd}.\n'
        return answer

    def forecast_errors(self, username=None, city_name=None):
        if username and city_name is None:
            answer = f'{username}, пожалуйста введите название города латиницей.\n'
        elif username is None and city_name:
            answer = f'<b>{str(city_name).capitalize()}</b> не найден!\n'
        answer += f'\U0001F537 Прогноз погоды по местоположению - "\U0001F310 {self.location_cmd}".\n'
        answer += f'\U0001F537 Помощь - {self.help_cmd}.\n'
        return answer

    def forecast_help(self, username, city_name):
        answer = f'{username}, введите название города латиницей.\n'
        answer += f'\U0001F537 Пример: <b>{city_name}</b>.\n'
        answer += f'\U0001F537 Прогноз погоды по местоположению - "\U0001F310 {self.location_cmd}".\n'
        answer += f'\U0001F537 Информации об авторе - {self.author_cmd}.\n'
        return answer

    def weather(self, username, location_details, weather_details):
        answer = f'{username}, в <b>{location_details["LocationName"]}</b>\n\n'
        answer += f'\U0001F539 <i>Часовой пояс:</i> <b>{location_details["TimeZone"]}</b>\n'
        answer += f'\U0001F539 <i>Дата:</i> \U0001F4C6 <b>{location_details["CurrentTime"].split()[0]}</b>\n'
        answer += f'\U0001F539 <i>Текущее время:</i> \U0000231A <b>{location_details["CurrentTime"].split()[-1].split(".")[0]}</b>\n'
        answer += f'\U0001F539 <i>Статус:</i> {weather_details["Icon"]} <b>{weather_details["DetailedStatus"]}</b>\n'
        answer += f'\U0001F539 <i>Температура воздуха:</i> \U0001F321 <b>{weather_details["Temp"]} {self.degree_sign}C</b>\n'
        answer += f'\U0001F539 <i>Давление:</i> <b>{weather_details["Pressure"]} мм</b>\n'
        answer += f'\U0001F539 <i>Влажность:</i> <b>{weather_details["Humidity"]} %</b>\n'
        answer += f'\U0001F539 <i>Скорость ветра:</i> <b>{weather_details["WindSpeed"]} м/c</b>\n\n'
        return answer

    def forecast_weather(self, username=None, location_details=None, weather_details=None):
        if username and location_details:
            answer = f'{username}, в <b>{location_details["LocationName"]}</b>\n'
            answer += f'\U0001F539 <i>Часовой пояс:</i> <b>{location_details["TimeZone"]}</b>\n\n'
        elif location_details and weather_details:
            answer = f'\U0001F539 <i>Дата:</i>\U0001F4C6 <b>{location_details["CurrentTime"].split()[0]}</b>\n'
            answer += f'\U0001F539 <i>Статус:</i> {weather_details["Icon"]} <b>{weather_details["DetailedStatus"]}</b>\n'
            answer += f'\U0001F539 <i>Температура воздуха:</i> \U0001F321 <b>{weather_details["Temp"]} {self.degree_sign}C</b>\n'
            answer += f'\U0001F539 <i>Давление:</i> <b>{weather_details["Pressure"]} мм</b>\n'
            answer += f'\U0001F539 <i>Влажность:</i> <b>{weather_details["Humidity"]} %</b>\n'
            answer += f'\U0001F539 <i>Скорость ветра:</i> <b>{weather_details["WindSpeed"]} м/c</b>\n\n'
        return answer

    def service_unavailable(self, username):
        answer = f'{username}, прошу прощения, в данный момент сервис погоды не доступен!\n'
        answer += 'Попробуйте позже\n'
        return answer