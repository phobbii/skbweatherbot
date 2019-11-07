#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import pyowm
import re
import random
import datetime
import timezonefinder
import pytz
import time
import os
import sys
import logging
import ssl
from aiohttp import web
import urllib.request

if 'OWN_KEY' in os.environ and os.environ['OWN_KEY'] is not None:
    OWN_KEY = os.environ['OWN_KEY']
else:
    sys.exit('OWN_KEY not exist or null')

if 'TELEBOT_KEY' in os.environ and os.environ['TELEBOT_KEY'] is not None:
    TELEBOT_KEY = os.environ['TELEBOT_KEY']
else:
    sys.exit('TELEBOT_KEY not exist or null')

WEBHOOK_HOST = None
WEBHOOK_SSL_CERT = None  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = None  # Path to the ssl private key
ip_services = ['https://ident.me', 'http://ipinfo.io/ip']
content_to_handle = ['text', 'location']
content_to_reject = ['audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact',
               'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
               'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id',
               'migrate_from_chat_id', 'pinned_message']

for service in ip_services:
    try:
        urllib.request.urlopen(service, timeout=1).read().decode('utf8')
    except Exception:
        print("Service {} unavailable".format(service))
    else:
        WEBHOOK_HOST = re.sub("^\s+|\n|\r|\s+$", '', urllib.request.urlopen(service).read().decode('utf8'))

for file in os.listdir('.'):
    for f in re.findall("\D+.pem", file):
        if f:
            WEBHOOK_SSL_CERT = os.path.abspath(f)
        else:
            sys.exit("SSL certificate not found")
    for f in re.findall("\D+.key", file):
        if f:
            WEBHOOK_SSL_PRIV = os.path.abspath(f)
        else:
            sys.exit("SSL key not found")

if WEBHOOK_HOST is None:
    sys.exit("WEBHOOK_HOST is None")
    
if WEBHOOK_SSL_CERT is None:
    sys.exit("WEBHOOK_SSL_CERT is None")

if WEBHOOK_SSL_PRIV is None:
    sys.exit("WEBHOOK_SSL_PRIV is None")    
    
if 'WEBHOOK_PORT' in os.environ and os.environ['WEBHOOK_PORT'] is not None:
    WEBHOOK_PORT = re.sub("^\s+|\n|\r|\s+$", '', os.environ['WEBHOOK_PORT'])
else:
    sys.exit('WEBHOOK_PORT not exist or null')
    
if 'WEBHOOK_LISTEN' in os.environ and os.environ['WEBHOOK_LISTEN'] is not None:
    WEBHOOK_LISTEN = os.environ['WEBHOOK_LISTEN']
else:
    sys.exit('WEBHOOK_LISTEN not exist or null')

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(TELEBOT_KEY)

owm = pyowm.OWM(API_key=OWN_KEY, language="ru")
bot = telebot.TeleBot(TELEBOT_KEY)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
app = web.Application()

# Process webhook calls
async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)

# Bot body
degree_sign = u'\N{DEGREE SIGN}'


def icon_handler(icon):
    if "01d" in icon:
        emoji = "\U00002600"
    elif "01n" in icon:
        emoji = "\U0001F311"
    elif "02" in icon:
        emoji = "\U000026C5"
    elif "03" in icon:
        emoji = "\U00002601"
    elif "04" in icon:
        emoji = "\U00002601"
    elif "09" in icon:
        emoji = "\U00002614"
    elif "10" in icon:
        emoji = "\U00002614"
    elif "11" in icon:
        emoji = "\U000026A1"
    elif "13" in icon:
        emoji = "\U00002744"
    elif "50" in icon:
        emoji = "\U0001F32B"
    return emoji


def send_action(message, action):
    while True:
        try:
            bot.send_chat_action(message, action)
            break
        except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ConnectionError) as e:
            print("{} - Sending again after 5 seconds".format(e))
            time.sleep(5)


def repeat_send_msg(message, answer, **kwargs):
    while True:
        try:
            bot.send_message(message, answer, **kwargs)
            break
        except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ConnectionError) as e:
            print("{} - Sending again after 5 seconds".format(e))
            time.sleep(5)


def send_msg(message, answer, **kwargs):
    kwargs_list=[i for i in kwargs.keys()]
    if "reply_markup" in kwargs_list and "parse_mode" in kwargs_list:
        repeat_send_msg(message, answer, reply_markup=kwargs["reply_markup"], parse_mode=kwargs["parse_mode"])
    elif "reply_markup" in kwargs_list:
        repeat_send_msg(message, answer, reply_markup=kwargs["reply_markup"])
    else:
        repeat_send_msg(message, answer)


def repeat_reply_to(message, answer, **kwargs):
    while True:
        try:
            bot.reply_to(message, answer, **kwargs)
            break
        except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ConnectionError) as e:
            print("{} - Sending again after 5 seconds".format(e))
            time.sleep(5)


def reply_to(message, answer, **kwargs):
    kwargs_list=[i for i in kwargs.keys()]
    if "reply_markup" in kwargs_list and "parse_mode" in kwargs_list:
        repeat_reply_to(message, answer, reply_markup=kwargs["reply_markup"], parse_mode=kwargs["parse_mode"])
    elif "reply_markup" in kwargs_list:
        repeat_reply_to(message, answer, reply_markup=kwargs["reply_markup"])
    else:
        repeat_reply_to(message, answer)


def repeat_send_sticker(message, answer, **kwargs):
    while True:
        try:
            bot.send_sticker(message, answer, **kwargs)
            break
        except (ConnectionAbortedError, ConnectionResetError, ConnectionRefusedError, ConnectionError) as e:
            print("{} - Sending again after 5 seconds".format(e))
            time.sleep(5)


def send_sticker(message, answer, **kwargs):
    kwargs_list=[i for i in kwargs.keys()]
    if "reply_to_message_id" in kwargs_list and "reply_markup" in kwargs_list:
        repeat_send_sticker(message, answer, reply_to_message_id=kwargs["reply_to_message_id"], reply_markup=kwargs["reply_markup"])
    else:
        repeat_send_sticker(message, answer)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
    forecast = telebot.types.InlineKeyboardButton(text="forecast", callback_data="forecast")
    help = telebot.types.InlineKeyboardButton(text="help", callback_data="help")
    autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="autor")
    keyboard.add(location,forecast, help, autor)
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    answer = "Привет {}.\n".format(username.title())
    answer += "\U0001F537 Введите город латиницей для получения погоды или\n"
    answer += "отправьте текущее местоположение - /location.\n"
    answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
    answer += "\U0001F537 Помощь - /help.\n"
    answer += "\U0001F537 Информации об авторе - /autor.\n"
    send_action(message.chat.id, 'typing')
    time.sleep(1)
    send_msg(message.chat.id, answer, reply_markup=keyboard)
    send_sticker(message.chat.id, 'CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ')


@bot.message_handler(commands=["location"])
def geo(message):
    reply_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location = telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True)
    reply_keyboard.add(location)
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    answer = "{}, нажмите на кнопку '\U0001F310 location' для отправки местоположение\n".format(username.title())
    send_action(message.chat.id, 'typing')
    time.sleep(1)
    send_msg(message.chat.id, answer, reply_markup=reply_keyboard)


@bot.message_handler(commands=["forecast"], content_types=content_to_handle)
def forecast(message):
    reply_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location = telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True)
    reply_keyboard.add(location)
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    answer = "{}, введите город для получения прогноза на 3 дня или\n".format(username.title())
    answer += "нажмите '\U0001F310 location' для отправки местоположение\n"
    send_action(message.chat.id, 'typing')
    time.sleep(1)
    send_msg(message.chat.id, answer, reply_markup=reply_keyboard)
    bot.register_next_step_handler(message, send_forecast_weather)


def send_forecast_weather(message):
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    if owm.is_API_online() == True:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        help = telebot.types.InlineKeyboardButton(text="help", callback_data="forecast_help")
        keyboard.add(help)
        if message.text is not None and bool(re.search('[\u0400-\u04FF]', message.text)) == True:
            answer = "{}, пожалуйста введите название города латиницей.\n".format(username.title())
            answer += "\U0001F537 Получения погоды по местоположению - '\U0001F310 location'.\n"
            answer += "\U0001F537 Помощь - help.\n"
            send_action(message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.chat.id, answer, reply_markup=keyboard)
            send_sticker(message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
            bot.register_next_step_handler(message, send_forecast_weather)
        elif message.text is not None and message.text == '...':
            answer = "<b>{}</b> не найден!\n".format(str(message.text).capitalize())
            answer += "\U0001F537 Получения погоды по местоположению - '\U0001F310 location'.\n"
            answer += "\U0001F537 Помощь - help.\n"
            send_action(message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
            bot.register_next_step_handler(message, send_forecast_weather)
        else:
            try:
                if message.location is not None:
                    forecast = owm.three_hours_forecast_at_coords(message.location.latitude, message.location.longitude)
                else:
                    forecast = owm.three_hours_forecast(message.text)
            except Exception:
                answer = "<b>{}</b> не найден!\n".format(str(message.text).capitalize())
                answer += "\U0001F537 Получения погоды по местоположению - '\U0001F310 location'.\n"
                answer += "\U0001F537 Помощь - help.\n"
                send_action(message.chat.id, 'typing')
                time.sleep(1)
                send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
                bot.register_next_step_handler(message, send_forecast_weather)
            else:
                location = forecast.get_forecast().get_location()
                tf = timezonefinder.TimezoneFinder()
                timezone_str = tf.certain_timezone_at(lat=location.get_lat(), lng=location.get_lon())
                if timezone_str is not None:
                    timezone = pytz.timezone(timezone_str)
                    dt = datetime.datetime.utcnow()
                    current_time = dt + timezone.utcoffset(dt)
                    answer = "{}, в <b>{}</b>\n".format(username.title(), location.get_name())
                    answer += "\U0001F539 <i>Часовой пояс:</i> <b>{}</b>\n\n".format(timezone_str)
                    for i in range(1, 4):
                        timer = current_time + datetime.timedelta(days=i, hours=0)
                        forecast_weather = forecast.get_weather_at(timer)
                        forecast_detailed_status = forecast_weather.get_detailed_status()
                        forecast_temp = int(forecast_weather.get_temperature('celsius')["temp"])
                        forecast_pressure = int(float(forecast_weather.get_pressure()['press']) * 0.75)
                        forecast_humidity = forecast_weather.get_humidity()
                        forecast_wind_speed = int(forecast_weather.get_wind()['speed'])
                        forecast_icon = icon_handler(forecast_weather.get_weather_icon_name())
                        answer += "\U0001F539 <i>Дата:</i>{} <b>{}</b>\n".format("\U0001F4C6", str(timer).split()[0])
                        answer += "\U0001F539 <i>Статус:</i> {} <b>{}</b>\n".format(forecast_icon, forecast_detailed_status.capitalize())
                        answer += "\U0001F539 <i>Температура воздуха:</i> {} <b>{} {}C</b>\n".format("\U0001F321", forecast_temp, degree_sign)
                        answer += "\U0001F539 <i>Давление:</i> <b>{} мм</b>\n".format(forecast_pressure)
                        answer += "\U0001F539 <i>Влажность:</i> <b>{} %</b>\n".format(forecast_humidity)
                        answer += "\U0001F539 <i>Скорость ветра:</i> <b>{} м/c</b>\n\n".format(forecast_wind_speed)
                send_action(message.chat.id, 'typing')
                time.sleep(1)
                reply_to(message, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
    else:
        stickers_list = ['CAADAgAD3gEAAvnkbAAB9tAurz2ipZUWBA',
                         'CAADAgADpQEAAvnkbAAB3LCoSz9i3NQWBA',
                         'CAADAgAD3AIAAvnkbAABZ4r6GvjutU4WBA',
                         'CAADAgAD4AIAAvnkbAABano-tB5DgtYWBA',
                         'CAADAgADYssAAmOLRgywPTPuHYqUWhYE',
                         'CAADAgADLgADNIWFDDKv5aCIOvtVFgQ',
                         'CAADAgADKAADNIWFDJH1ZYPnRgPgFgQ'
                         ]
        answer = "{}, прошу прощения, в данный момент сервис погоды не доступен!\n".format(username)
        answer += "Попробуйте позже\n"
        send_action(message.chat.id, 'typing')
        time.sleep(1)
        send_msg(message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False,))
        send_sticker(message.chat.id, random.choice(stickers_list))


@bot.message_handler(commands=['help'])
def send_help(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
    forecast = telebot.types.InlineKeyboardButton(text="forecast", callback_data="forecast")
    autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="autor")
    keyboard.add(location, forecast, autor)
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    answer = "{}, введите название города латиницей.\n".format(username.title())
    answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
    answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
    answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
    answer += "\U0001F537 Информации об авторе - /autor.\n"
    send_action(message.chat.id, 'typing')
    time.sleep(1)
    send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
    send_sticker(message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')


@bot.message_handler(commands=['autor'])
def send_autor(message):
    answer = "\U0001F537 Автор: <b>Eugene Skiba</b>\n"
    answer += "\U0001F537 Почта: skiba.eugene@gmail.com\n"
    answer += "\U0001F537 Телеграм: @phobbii"
    send_action(message.chat.id, 'typing')
    time.sleep(1)
    send_msg(message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
    send_sticker(message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')


@bot.callback_query_handler(func=lambda message: True)
def callback_inline(message):
    if message.message:
        if message.from_user.first_name is not None:
            username = message.from_user.first_name
        else:
            username = message.from_user.username
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        if message.data == "help":
            location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
            forecast = telebot.types.InlineKeyboardButton(text="forecast", callback_data="forecast")
            autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="autor")
            keyboard.add(location, forecast, autor)
            answer = "{}, введите название города латиницей.\n".format(username.title())
            answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
            answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
            answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
            answer += "\U0001F537 Информации об авторе - /autor.\n"
            send_action(message.message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(message.message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')
        elif message.data == "autor":
            answer = "\U0001F537 Автор: <b>Eugene Skiba</b>\n"
            answer += "\U0001F537 Почта: skiba.eugene@gmail.com\n"
            answer += "\U0001F537 Телеграм: @phobbii"
            send_action(message.message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
            send_sticker(message.message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')
        elif message.data == "location":
            reply_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            location = telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True)
            reply_keyboard.add(location)
            answer = "{}, нажмите на кнопку '\U0001F310 location' для отправки местоположение\n".format(username.title())
            send_action(message.message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.message.chat.id, answer, reply_markup=reply_keyboard)
        elif message.data == "forecast":
            reply_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            location = telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True)
            reply_keyboard.add(location)
            answer = "{}, введите город для получения прогноза на 3 дня или\n".format(username.title())
            answer += "нажмите '\U0001F310 location' для отправки местоположение\n"
            send_action(message.message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.message.chat.id, answer, reply_markup=reply_keyboard)
            bot.register_next_step_handler(message.message, send_forecast_weather)
        elif message.data == "forecast_help":
            autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="forecast_autor")
            keyboard.add(autor)
            answer = "{}, введите название города латиницей.\n".format(username.title())
            answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
            answer += "\U0001F537 Получения погоды по местоположению - '\U0001F310 location'.\n"
            answer += "\U0001F537 Информации об авторе - autor.\n"
            send_action(message.message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(message.message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')
        elif message.data == "forecast_autor":
            answer = "\U0001F537 Автор: <b>Eugene Skiba</b>\n"
            answer += "\U0001F537 Почта: skiba.eugene@gmail.com\n"
            answer += "\U0001F537 Телеграм: @phobbii"
            send_action(message.message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.message.chat.id, answer, parse_mode='HTML')
            send_sticker(message.message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')


@bot.message_handler(func=lambda message: True, content_types=content_to_handle)
def send_weather(message):
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    if owm.is_API_online() == True:
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
        location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
        forecast = telebot.types.InlineKeyboardButton(text="forecast", callback_data="forecast")
        help = telebot.types.InlineKeyboardButton(text="help", callback_data="help")
        keyboard.add(location, forecast, help)
        if message.text is not None and bool(re.search('[\u0400-\u04FF]', message.text)) == True:
            answer = "{}, пожалуйста введите название города латиницей.\n".format(username.title())
            answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
            answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
            answer += "\U0001F537 Помощь - /help.\n"
            send_action(message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.chat.id, answer, reply_markup=keyboard)
            send_sticker(message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
        elif message.text is not None and message.text == '...':
            answer = "<b>{}</b> не найден!\n".format(str(message.text).capitalize())
            answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
            answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
            answer += "\U0001F537 Помощь - /help.\n"
            send_action(message.chat.id, 'typing')
            time.sleep(1)
            send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
        else:
            try:
                if message.location is not None:
                    observation = owm.weather_at_coords(message.location.latitude, message.location.longitude)
                else:
                    observation = owm.weather_at_place(message.text)
            except Exception:
                answer = "<b>{}</b> не найден!\n".format(str(message.text).capitalize())
                answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
                answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
                answer += "\U0001F537 Помощь - /help.\n"
                send_action(message.chat.id, 'typing')
                time.sleep(1)
                send_msg(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
            else:
                location = observation.get_location()
                tf = timezonefinder.TimezoneFinder()
                timezone_str = tf.certain_timezone_at(lat=location.get_lat(), lng=location.get_lon())
                icon = icon_handler(observation.get_weather().get_weather_icon_name())
                detailed_status = observation.get_weather().get_detailed_status()
                temp = int(observation.get_weather().get_temperature('celsius')["temp"])
                pressure = int(float(observation.get_weather().get_pressure()['press']) * 0.75)
                humidity = observation.get_weather().get_humidity()
                wind_speed = observation.get_weather().get_wind()['speed']
                answer = "{}, в <b>{}</b>\n\n".format(username.title(), location.get_name())
                if timezone_str is not None:
                    timezone = pytz.timezone(timezone_str)
                    dt = datetime.datetime.utcnow()
                    current_time = dt + timezone.utcoffset(dt)
                    answer += "\U0001F539 <i>Часовой пояс:</i> <b>{}</b>\n".format(timezone_str)
                    answer += "\U0001F539 <i>Дата:</i> {} <b>{}</b>\n".format("\U0001F4C6", str(current_time).split()[0])
                    answer += "\U0001F539 <i>Текущее время:</i> {} <b>{}</b>\n".format("\U0000231A", str(current_time).split()[-1].split('.')[0])
                answer += "\U0001F539 <i>Статус:</i> {} <b>{}</b>\n".format(icon, detailed_status.capitalize())
                answer += "\U0001F539 <i>Температура воздуха:</i> {} <b>{} {}C</b>\n".format("\U0001F321", temp, degree_sign)
                answer += "\U0001F539 <i>Давление:</i> <b>{} мм</b>\n".format(pressure)
                answer += "\U0001F539 <i>Влажность:</i> <b>{} %</b>\n".format(humidity)
                answer += "\U0001F539 <i>Скорость ветра:</i> <b>{} м/c</b>\n\n".format(wind_speed)
                send_action(message.chat.id, 'typing')
                time.sleep(1)
                reply_to(message, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
    else:
        stickers_list = ['CAADAgAD3gEAAvnkbAAB9tAurz2ipZUWBA',
                         'CAADAgADpQEAAvnkbAAB3LCoSz9i3NQWBA',
                         'CAADAgAD3AIAAvnkbAABZ4r6GvjutU4WBA',
                         'CAADAgAD4AIAAvnkbAABano-tB5DgtYWBA',
                         'CAADAgADYssAAmOLRgywPTPuHYqUWhYE',
                         'CAADAgADLgADNIWFDDKv5aCIOvtVFgQ',
                         'CAADAgADKAADNIWFDJH1ZYPnRgPgFgQ'
                         ]
        answer = "{}, прошу прощения, в данный момент сервис погоды не доступен!\n".format(username)
        answer += "Попробуйте позже\n"
        send_action(message.chat.id, 'typing')
        time.sleep(1)
        send_msg(message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))
        send_sticker(message.chat.id, random.choice(stickers_list))


@bot.message_handler(func=lambda message: True, content_types=content_to_reject)
def wrong_content(message):
    stickers_list = ['CAADAgAD4QIAAvnkbAAB4uG83jqZC7oWBA',
                     'CAADAgADdgIAAvnkbAABwOWRNMVkWAwWBA',
                     'CAADAgADAQIAAvnkbAABgYkUR2jzKikWBA',
                     'CAADAgAD2wEAAvnkbAABCX-hVktjtVAWBA',
                     'CAADAgADwAEAAvnkbAABoDH6R5pwO0cWBA',
                     'CAADAgADvwEAAvnkbAABHngR9XeKmpsWBA',
                     'CAADAgADtAEAAvnkbAABLH9k4WvwzJgWBA',
                     'CAADAgADOgIAAvnkbAABRlHfrrHgNBcWBA',
                     'CAADAgADagEAAvnkbAABiDcDQFCEuXgWBA',
                     'CAADAgADJAEAAvnkbAAB2fxXBcKZT08WBA',
                     'CAADAgADNAEAAvnkbAABdiR2Dg6Dxc8WBA'
                     ]
    send_sticker(message.chat.id, random.choice(stickers_list), reply_to_message_id=message.message_id, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
web.run_app( app, host=WEBHOOK_LISTEN, port=WEBHOOK_PORT, ssl_context=context,)