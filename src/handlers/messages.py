"""Message handlers for the bot."""
import time
import re
import random
import telebot
from utils.bot_helpers import (
    send_action, send_message, send_sticker, get_username,
    create_inline_keyboard, remove_keyboard, reply_to_message
)
from services.weather_service import WeatherService
from config import ERROR_STICKERS, WRONG_CONTENT_STICKERS


class MessageHandlers:
    """Handlers for bot messages."""
    
    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService):
        """Initialize handlers with bot and weather service."""
        self.bot = bot
        self.weather = weather_service
    
    def handle_weather_request(self, message: telebot.types.Message) -> None:
        """Handle weather request by city or location."""
        username = get_username(message)
        
        if not self.weather.is_online():
            self._send_service_unavailable(message, username)
            return
        
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help")
        )
        
        # Check for Cyrillic
        if message.text and re.search(r'[\u0400-\u04FF]', message.text):
            answer = f"{username.title()}, пожалуйста введите название города латиницей.\n"
            answer += "\U0001F537 Прогноз погоды по местоположению - /location.\n"
            answer += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
            answer += "\U0001F537 Помощь - /help.\n"
            send_action(self.bot, message.chat.id, 'typing')
            time.sleep(1)
            send_message(self.bot, message.chat.id, answer, reply_markup=keyboard)
            send_sticker(self.bot, message.chat.id, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA')
            return
        
        # Check for invalid input
        if message.text == '...':
            answer = f"<b>{message.text.capitalize()}</b> не найден!\n"
            answer += "\U0001F537 Прогноз погоды по местоположению - /location.\n"
            answer += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
            answer += "\U0001F537 Помощь - /help.\n"
            send_action(self.bot, message.chat.id, 'typing')
            time.sleep(1)
            send_message(self.bot, message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(self.bot, message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
            return
        
        # Get weather
        if message.location:
            weather_data = self.weather.get_current_weather(lat=message.location.latitude, lon=message.location.longitude)
        else:
            weather_data = self.weather.get_current_weather(city=message.text)
        
        if not weather_data:
            city_name = message.text.capitalize() if message.text else "..."
            answer = f"<b>{city_name}</b> не найден!\n"
            answer += "\U0001F537 Прогноз погоды по местоположению - /location.\n"
            answer += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
            answer += "\U0001F537 Помощь - /help.\n"
            send_action(self.bot, message.chat.id, 'typing')
            time.sleep(1)
            send_message(self.bot, message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
            send_sticker(self.bot, message.chat.id, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA')
            return
        
        answer = self.weather.format_current_weather(username.title(), weather_data)
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
    
    def handle_wrong_content(self, message: telebot.types.Message) -> None:
        """Handle unsupported content types."""
        send_sticker(self.bot, message.chat.id, random.choice(WRONG_CONTENT_STICKERS),
                    reply_to_message_id=message.message_id, reply_markup=remove_keyboard())
    
    def _send_service_unavailable(self, message: telebot.types.Message, username: str) -> None:
        """Send service unavailable message."""
        answer = f"{username}, прошу прощения, в данный момент сервис погоды не доступен!\n"
        answer += "Попробуйте позже\n"
        send_action(self.bot, message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, message.chat.id, answer, reply_markup=remove_keyboard())
        send_sticker(self.bot, message.chat.id, random.choice(ERROR_STICKERS))
