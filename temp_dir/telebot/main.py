import telebot, re, random
from datetime import datetime, timedelta
from ..handlers.main import Messages
from ..generators.main import Answers
from ..weather.main import Weather


class Telebot(object):

    def __init__(self, telebot_auth, owm_auth, owm_language='ru', sleep_timer=5, location_cmd='location', 
               forecast_cmd='forecast', help_cmd='help', author_cmd='author'):
        self.messages = Messages(telebot_auth, sleep_timer)
        self.answers = Answers()
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

    def welcome(self, message, sticker_id='CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ'):
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        location_button = telebot.types.InlineKeyboardButton(text='location', callback_data='location')
        forecast_button = telebot.types.InlineKeyboardButton(text='forecast', callback_data='forecast')
        help_button = telebot.types.InlineKeyboardButton(text='help', callback_data='help')
        author_button = telebot.types.InlineKeyboardButton(text='author', callback_data='author')
        keyboard.add(location_button, forecast_button, help_button, author_button)
        username = self.__get_username(message)
        answer = self.answers.welcome_help(self, username, self.location_cmd, self.forecast_cmd, 
                                         self.help_cmd, self.author_cmd)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)
        self.messages.send_sticker(message.chat.id, sticker_id)

    def geo(self, message):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        location_button = telebot.types.KeyboardButton(text=f'\U0001F310 {self.location_cmd}', 
                                                     request_location=True)
        keyboard.add(location_button)
        username = self.__get_username(message)
        answer = self.answers.geo(username, self.location_cmd)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)

    def forecast(self, message):
        keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        location_button = telebot.types.KeyboardButton(text=f'\U0001F310 {self.location_cmd}', 
                                                     request_location=True)
        keyboard.add(location_button)
        username = self.__get_username(message)
        answer = self.answers.forecast(username, self.forecast_cmd)
        self.messages.send_action(message.chat.id, 'typing')
        self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)
        self.bot.register_next_step_handler(message, self.send_forecast_weather)

    def send_forecast_weather(self, message):
        username = self.__get_username(message)
        if self.weather.is_online():
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            help = telebot.types.InlineKeyboardButton(text='help', callback_data='forecast_help')
            keyboard.add(help)
            if message.text is not None and bool(re.search('[\u0400-\u04FF]', message.text)):
                answer = self.answers.forecast_errors(username=username)
                self.messages.send_action(message.chat.id, 'typing')
                self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard)
                self.messages.send_sticker(message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
                self.bot.register_next_step_handler(message, self.send_forecast_weather)
            elif message.text is not None and message.text == '...':
                answer = self.answers.forecast_errors(city_name=str(message.text).capitalize())
                self.messages.send_action(message.chat.id, 'typing')
                self.messages.send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                self.messages.send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
                self.bot.bot.register_next_step_handler(message, self.send_forecast_weather)
            else:
                forecast_data = self.weather.get_data(message, forecast=True)
                if forecast_data:
                    pass