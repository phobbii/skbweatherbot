"""Command handlers for the bot."""
import time
import re
import random
import telebot
from utils.bot_helpers import (
    send_action, send_message, send_sticker, get_username,
    create_inline_keyboard, create_location_keyboard, remove_keyboard
)
from services.weather_service import WeatherService
from config import ERROR_STICKERS


class CommandHandlers:
    """Handlers for bot commands."""
    
    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService):
        """Initialize handlers with bot and weather service."""
        self.bot = bot
        self.weather = weather_service
    
    def handle_start(self, message: telebot.types.Message) -> None:
        """Handle /start command."""
        username = get_username(message)
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help"),
            ("author", "author")
        )
        
        answer = f"Привет {username.title()}.\n"
        answer += "\U0001F537 Введите город латиницей для получения погоды или\n"
        answer += "отправьте текущее местоположение - /location.\n"
        answer += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
        answer += "\U0001F537 Помощь - /help.\n"
        answer += "\U0001F537 Информации об авторе - /author.\n"
        
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=keyboard)
        send_sticker(self.bot, message.chat.id, 'CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ')
    
    def handle_location(self, message: telebot.types.Message) -> None:
        """Handle /location command."""
        username = get_username(message)
        keyboard = create_location_keyboard()
        answer = f"{username.title()}, нажмите на кнопку '\U0001F310 location' для отправки местоположения\n"
        
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=keyboard)
    
    def handle_forecast_command(self, message: telebot.types.Message) -> None:
        """Handle /forecast command."""
        username = get_username(message)
        keyboard = create_location_keyboard()
        answer = f"{username.title()}, введите город для получения прогноза на 5 дней или\n"
        answer += "нажмите '\U0001F310 location' для отправки местоположения\n"
        
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=keyboard)
        self.bot.register_next_step_handler(message, self.handle_forecast_input)
    
    def handle_forecast_input(self, message: telebot.types.Message) -> None:
        """Handle forecast input (city or location)."""
        username = get_username(message)
        
        if not self.weather.is_online():
            self._send_service_unavailable(message, username)
            return
        
        keyboard = create_inline_keyboard(("help", "forecast_help"))
        
        # Check for Cyrillic
        if message.text and re.search(r'[\u0400-\u04FF]', message.text):
            answer = f"{username.title()}, пожалуйста введите название города латиницей.\n"
            answer += "\U0001F537 Прогноз по местоположению - '\U0001F310 location'.\n"
            answer += "\U0001F537 Помощь - help.\n"
            send_action(self.bot, message.chat.id, 'typing')
            time.sleep(1)
            send_message(self.bot, message.chat.id, answer, reply_markup=keyboard)
            send_sticker(self.bot, message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return
        
        # Get forecast
        if message.location:
            forecast_data = self.weather.get_forecast(lat=message.location.latitude, lon=message.location.longitude)
        else:
            forecast_data = self.weather.get_forecast(city=message.text)
        
        if not forecast_data:
            city_name = message.text.capitalize() if message.text else "..."
            answer = f"<b>{city_name}</b> не найден!\n"
            answer += "\U0001F537 Прогноз по местоположению - '\U0001F310 location'.\n"
            answer += "\U0001F537 Помощь - help.\n"
            send_action(self.bot, message.chat.id, 'typing')
            time.sleep(1)
            send_message(self.bot, message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(self.bot, message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return
        
        answer = self.weather.format_forecast(username.title(), forecast_data)
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        from utils.bot_helpers import reply_to_message
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
    
    def handle_help(self, message: telebot.types.Message) -> None:
        """Handle /help command."""
        username = get_username(message)
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("author", "author")
        )
        
        answer = f"{username.title()}, введите название города латиницей.\n"
        answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
        answer += "\U0001F537 Прогноз по местоположению - /location.\n"
        answer += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
        answer += "\U0001F537 Информации об авторе - /author.\n"
        
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
        send_sticker(self.bot, message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')
    
    def handle_author(self, message: telebot.types.Message) -> None:
        """Handle /author command."""
        answer = "\U0001F537 Author: <b>Yevhen Skyba</b>\n"
        answer += "\U0001F537 Email: skiba.eugene@gmail.com\n"
        answer += "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
        answer += "\U0001F537 Telegram: @phobbii"
        
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
        send_sticker(self.bot, message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')
    
    def _send_service_unavailable(self, message: telebot.types.Message, username: str) -> None:
        """Send service unavailable message."""
        answer = f"{username}, прошу прощения, в данный момент сервис погоды не доступен!\n"
        answer += "Попробуйте позже\n"
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=remove_keyboard())
        send_sticker(self.bot, message.chat.id, random.choice(ERROR_STICKERS))
