"""Message handlers for the bot."""
import re
import random
import telebot
from utils.bot_helpers import create_inline_keyboard, remove_keyboard, reply_to_message, send_sticker, is_emoji
from services.weather_service import WeatherService
from config import WRONG_CONTENT_STICKERS
from handlers.base import BaseHandler


class MessageHandlers(BaseHandler):
    """Handlers for bot messages."""
    
    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService):
        """Initialize handlers with bot and weather service."""
        super().__init__(bot)
        self.weather = weather_service
    
    def handle_weather_request(self, message: telebot.types.Message) -> None:
        """Handle weather request by city or location."""
        username = self.get_username(message)
        
        if not self.weather.is_online():
            self.send_service_unavailable(message.chat.id, username, reply_markup=remove_keyboard())
            return
        
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help")
        )

        # Check for emoji in text
        if message.text and is_emoji(message.text):
            self.handle_wrong_content(message)
            return

        # Check for invalid input
        if message.text == '...':
            self.send_city_not_found(message.chat.id, message.text.capitalize(), keyboard)
            return
        
        # Get weather
        if message.location:
            weather_data = self.weather.get_current_weather(lat=message.location.latitude, lon=message.location.longitude)
        else:
            weather_data = self.weather.get_current_weather(city=message.text)
        
        if not weather_data:
            city_name = message.text.capitalize() if message.text else "..."
            self.send_city_not_found(message.chat.id, city_name, keyboard)
            return
        
        answer = self.weather.format_current_weather(username.title(), weather_data)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
    
    def handle_wrong_content(self, message: telebot.types.Message) -> None:
        """Handle unsupported content types."""
        send_sticker(self.bot, message.chat.id, random.choice(WRONG_CONTENT_STICKERS),
                    reply_to_message_id=message.message_id, reply_markup=remove_keyboard())
