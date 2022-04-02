import telebot, re, random, pytz
from datetime import datetime, timedelta
from tzwhere import tzwhere
from ..handlers.main import Messages
from ..generators.main import Answers
from ..weather.main import Weather


class Telebot(object):

    def __init__(self, telebot_auth, owm_auth, owm_language='ru', author_name, author_email, author_linkedin, author_tg,
                sleep_timer=5, location_cmd='location', forecast_cmd='forecast', help_cmd='help', author_cmd='author'):
        self.messages = Messages(telebot_auth, sleep_timer)
        self.answers = Answers(author_name, author_email, author_linkedin, author_tg, 
                            location_cmd, forecast_cmd, help_cmd, author_cmd)
        self.weather = Weather(API_key=owm_auth, language=owm_language)
        self.bot = telebot_auth
        self.location_cmd = location_cmd
        self.forecast_cmd = forecast_cmd
        self.help_cmd = help_cmd
        self.author_cmd = author_cmd

    def __get_username(message):
        if message.from_user.first_name is not None:
            username = message.from_user.first_name
        else:
            username = message.from_user.username
        return username.title()

    def __service_unavailable(self, username, message):
        stickers_list = ['CAADAgAD3gEAAvnkbAAB9tAurz2ipZUWBA',
                        'CAADAgADpQEAAvnkbAAB3LCoSz9i3NQWBA',
                        'CAADAgAD3AIAAvnkbAABZ4r6GvjutU4WBA',
                        'CAADAgAD4AIAAvnkbAABano-tB5DgtYWBA',
                        'CAADAgADYssAAmOLRgywPTPuHYqUWhYE',
                        'CAADAgADLgADNIWFDDKv5aCIOvtVFgQ',
                        'CAADAgADKAADNIWFDJH1ZYPnRgPgFgQ']
        answer = self.answers.service_unavailable(username)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, 
                            reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))
        self.messages.send_sticker(message.chat.id, random.choice(stickers_list))

    def welcome(self, message):
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        location_button = telebot.types.InlineKeyboardButton(text='location', callback_data='location')
        forecast_button = telebot.types.InlineKeyboardButton(text='forecast', callback_data='forecast')
        help_button = telebot.types.InlineKeyboardButton(text='help', callback_data='help')
        author_button = telebot.types.InlineKeyboardButton(text='author', callback_data='author')
        keyboard.add(location_button, forecast_button, help_button, author_button)
        username = self.__get_username(message)
        answer = self.answers.welcome_help(self, username)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)
        self.messages.send_sticker(message.chat.id, 'CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ')

    def geo(self, message):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        location_button = telebot.types.KeyboardButton(text=f'\U0001F310 {self.location_cmd}', 
                                                     request_location=True)
        keyboard.add(location_button)
        username = self.__get_username(message)
        answer = self.answers.geo(username)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)

    def forecast(self, message):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        location_button = telebot.types.KeyboardButton(text=f'\U0001F310 {self.location_cmd}', 
                                                     request_location=True)
        keyboard.add(location_button)
        username = self.__get_username(message)
        answer = self.answers.forecast(username)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)
        self.bot.register_next_step_handler(message, self.send_forecast_weather)

    def send_forecast_weather(self, message):
        username = self.__get_username(message)
        if self.weather.is_online():
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            help = telebot.types.InlineKeyboardButton(text='help', callback_data='forecast_help')
            keyboard.add(help)
            if message.text and bool(re.search('[\u0400-\u04FF]', message.text)):
                answer = self.answers.forecast_errors(username=username)
                self.messages.send_action(message.chat.id, 'typing')
                self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)
                self.messages.send_sticker(message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
                self.bot.register_next_step_handler(message, self.send_forecast_weather)
            elif message.text and message.text == '...':
                answer = self.answers.forecast_errors(city_name=str(message.text).capitalize())
                self.messages.send_action(message.chat.id, 'typing')
                self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                self.messages.send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
                self.bot.register_next_step_handler(message, self.send_forecast_weather)
            else:
                forecast_data = self.weather.get_data(message, forecast=True)
                if forecast_data:
                    location = forecast_data[1]
                    tf = tzwhere.tzwhere()
                    timezone_str = tf.tzNameAt(location.get_lat(), location.get_lon())
                    timezone = pytz.timezone(timezone_str)
                    dt = datetime.utcnow()
                    current_time = dt + timezone.utcoffset(dt)
                    answer = self.answers.forecast_weather(username=username, 
                                                        location_name=location.get_name(), tzone=timezone_str)
                    for i in range(1, 4):
                        timer = current_time + datetime.timedelta(days=i, hours=0)
                        forecast_weather = self.weather.get_weather(forecast_data, timer=timer)
                        answer += self.answers.forecast_weather(date=str(timer).split()[0], icon=forecast_weather['Icon'], 
                                                                detailed_status=forecast_weather['DetailedStatus'], 
                                                                temp=forecast_weather['Temp'], 
                                                                pressure=forecast_weather['Pressure'], 
                                                                humidity=forecast_weather['Humidity'], 
                                                                wind_speed=forecast_weather['WindSpeed'])
                    self.messages.send_action(message.chat.id, 'typing')
                    self.messages.reply_to(message, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), 
                                        parse_mode='HTML')
                else:
                    answer = self.answers.forecast_errors(city_name=str(message.text).capitalize())
                    self.messages.send_action(message.chat.id, 'typing')
                    self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                    self.messages.send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
                    self.bot.register_next_step_handler(message, self.send_forecast_weather)
        else:
            self.__service_unavailable(username, message)