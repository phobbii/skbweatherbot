"""Message handlers for the bot."""
import random

import telebot

from config import WRONG_CONTENT_STICKERS
from handlers.base import BaseHandler
from services.weather_service import WeatherService
from utils.bot_helpers import (
    create_inline_keyboard,
    is_emoji,
    remove_keyboard,
    reply_to_message,
    send_sticker,
)


class MessageHandlers(BaseHandler):
    """Handlers for free-text and location messages."""

    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService) -> None:
        super().__init__(bot)
        self.weather = weather_service

    def handle_weather_request(self, message: telebot.types.Message) -> None:
        """Handle weather request by city name or shared location."""
        username = self.get_username(message)

        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help"),
        )

        if message.text and is_emoji(message.text):
            self.handle_wrong_content(message)
            return

        if message.text == "...":
            self.send_city_not_found(message.chat.id, message.text, keyboard)
            return

        if message.location:
            weather_data = self.weather.get_current_weather(lat=message.location.latitude, lon=message.location.longitude)
        else:
            weather_data = self.weather.get_current_weather(city=message.text)

        if not weather_data:
            city_name = message.text.capitalize() if message.text else "..."
            self.send_city_not_found(message.chat.id, city_name, keyboard)
            return

        answer = self.weather.format_current_weather(username, weather_data)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode="HTML")

    def handle_wrong_content(self, message: telebot.types.Message) -> None:
        """Reply with a random sticker for unsupported content."""
        send_sticker(
            self.bot,
            message.chat.id,
            random.choice(WRONG_CONTENT_STICKERS),
            reply_to_message_id=message.message_id,
            reply_markup=remove_keyboard(),
        )
