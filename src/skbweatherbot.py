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

if 'OWN_KEY' in os.environ and os.environ['OWN_KEY'] is not None:
    OWN_KEY = os.environ['OWN_KEY']
else:
    sys.exit('OWN_KEY not exist or null')

if 'TELEBOT_KEY' in os.environ and os.environ['TELEBOT_KEY'] is not None:
    TELEBOT_KEY = os.environ['TELEBOT_KEY']
else:
    sys.exit('TELEBOT_KEY not exist or null')

owm = pyowm.OWM(API_key=OWN_KEY, language="ru")
bot = telebot.TeleBot(TELEBOT_KEY)

content_to_handle = ['text', 'location']
content_to_reject = ['audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact',
               'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
               'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id',
               'migrate_from_chat_id', 'pinned_message']

@bot.message_handler(commands=['start'])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
    help = telebot.types.InlineKeyboardButton(text="help", callback_data="help")
    autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="autor")
    keyboard.add(location, help, autor)
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    answer = "Привет {}.\n".format(username.title())
    answer += "\U0001F537 Введите город латиницей для получения погоды или\n"
    answer += "отправьте текущее местоположение - /location.\n"
    answer += "\U0001F537 Помощь - /help.\n"
    answer += "\U0001F537 Информации об авторе - /autor.\n"
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(message.chat.id, answer, reply_markup=keyboard)
    bot.send_sticker(message.chat.id, 'CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ')

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
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(message.chat.id, answer, reply_markup=reply_keyboard)

@bot.message_handler(commands=['help'])
def send_help(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
    autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="autor")
    keyboard.add(location, autor)
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    answer = "{}, введите название города латиницей.\n".format(username.title())
    answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
    answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
    answer += "\U0001F537 Информации об авторе - /autor.\n"
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
    bot.send_sticker(message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')

@bot.message_handler(commands=['autor'])
def send_autor(message):
    answer = "\U0001F537 Автор: <b>Eugene Skiba</b>\n"
    answer += "\U0001F537 Почта: skiba.eugene@gmail.com\n"
    answer += "\U0001F537 Телеграм: @phobbii"
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(1)
    bot.send_message(message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
    bot.send_sticker(message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')

@bot.callback_query_handler(func=lambda message: True)
def callback_inline(message):
    if message.message:
        if message.from_user.first_name is not None:
            username = message.from_user.first_name
        else:
            username = message.from_user.username
        if message.data == "help":
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
            autor = telebot.types.InlineKeyboardButton(text="autor", callback_data="autor")
            keyboard.add(location, autor)
            answer = "{}, введите название города латиницей.\n".format(username.title())
            answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
            answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
            answer += "\U0001F537 Информации об авторе - /autor.\n"
            bot.send_chat_action(message.message.chat.id, 'typing')
            time.sleep(1)
            bot.send_message(message.message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            bot.send_sticker(message.message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')
        elif message.data == "autor":
            answer = "\U0001F537 Автор: <b>Eugene Skiba</b>\n"
            answer += "\U0001F537 Почта: skiba.eugene@gmail.com\n"
            answer += "\U0001F537 Телеграм: @phobbii"
            bot.send_chat_action(message.message.chat.id, 'typing')
            time.sleep(1)
            bot.send_message(message.message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
            bot.send_sticker(message.message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')
        elif message.data == "location":
            reply_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            location = telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True)
            reply_keyboard.add(location)
            answer = "{}, нажмите на кнопку '\U0001F310 location' для отправки местоположение\n".format(username.title())
            bot.send_chat_action(message.message.chat.id, 'typing')
            time.sleep(1)
            bot.send_message(message.message.chat.id, answer, reply_markup=reply_keyboard)

@bot.message_handler(func=lambda message: True, content_types=content_to_handle)
def send_weather(message):
    if message.from_user.first_name is not None:
        username = message.from_user.first_name
    else:
        username = message.from_user.username
    if owm.is_API_online() == True:
            if message.text is not None and bool(re.search('[\u0400-\u04FF]', message.text)) == True:
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
                help = telebot.types.InlineKeyboardButton(text="help", callback_data="help")
                keyboard.add(location, help)
                answer = "{}, пожалуйста введите название города латиницей.\n".format(username.title())
                answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
                answer += "\U0001F537 Помощь - /help.\n"
                bot.send_chat_action(message.chat.id, 'typing')
                time.sleep(1)
                bot.send_message(message.chat.id, answer, reply_markup=keyboard)
                bot.send_sticker(message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
            elif message.text is not None and message.text == '...':
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
                help = telebot.types.InlineKeyboardButton(text="help", callback_data="help")
                keyboard.add(location, help)
                answer = "<b>{}</b> не найден!\n".format(str(message.text).capitalize())
                answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
                answer += "\U0001F537 Помощь - /help.\n"
                bot.send_chat_action(message.chat.id, 'typing')
                time.sleep(1)
                bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                bot.send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
            else:
                try:
                    if message.location is not None:
                        observation = owm.weather_at_coords(message.location.latitude, message.location.longitude)
                    else:
                        observation = owm.weather_at_place(message.text)
                except Exception:
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                    location = telebot.types.InlineKeyboardButton(text="location", callback_data="location")
                    help = telebot.types.InlineKeyboardButton(text="help", callback_data="help")
                    keyboard.add(location, help)
                    answer = "<b>{}</b> не найден!\n".format(str(message.text).capitalize())
                    answer += "\U0001F537 Получения погоды по местоположению - /location.\n"
                    answer += "\U0001F537 Помощь - /help.\n"
                    bot.send_chat_action(message.chat.id, 'typing')
                    time.sleep(1)
                    bot.send_message(message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
                    bot.send_sticker(message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
                else:
                    location = observation.get_location()
                    tf = timezonefinder.TimezoneFinder()
                    timezone_str = tf.certain_timezone_at(lat=location.get_lat(), lng=location.get_lon())
                    icon = observation.get_weather().get_weather_icon_name()
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
                    answer += "\U0001F539 <i>Статус:</i> {} <b>{}</b>\n".format(emoji, detailed_status.capitalize())
                    answer += "\U0001F539 <i>Температура воздуха:</i> {} <b>{} ℃</b>\n".format("\U0001F321", temp)
                    answer += "\U0001F539 <i>Давление:</i> <b>{} мм</b>\n".format(pressure)
                    answer += "\U0001F539 <i>Влажность:</i> <b>{} %</b>\n".format(humidity)
                    answer += "\U0001F539 <i>Скорость ветра:</i> <b>{} м/c</b>\n".format(wind_speed)
                    bot.send_chat_action(message.chat.id, 'typing')
                    time.sleep(1)
                    bot.reply_to(message, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False), parse_mode='HTML')
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
        bot.send_chat_action(message.chat.id, 'typing')
        time.sleep(1)
        bot.send_message(message.chat.id, answer, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False,))
        bot.send_sticker(message.chat.id, random.choice(stickers_list))

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
    bot.send_sticker(message.chat.id, random.choice(stickers_list), reply_to_message_id=message.message_id, reply_markup=telebot.types.ReplyKeyboardRemove(selective=False))

while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except Exception as error:
        print(error)
        time.sleep(10)