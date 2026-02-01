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
    """Class to handle incoming bot messages."""

    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService):
        """Initialize the message handler with a bot instance and weather service."""
        self.bot = bot
        self.weather = weather_service

    @staticmethod
    def _help_text() -> str:
        """Return a standard help text with commands."""
        return (
            "\U0001F537 Прогноз по местоположению - /location.\n"
            "\U0001F537 Прогноз на 5 дней - /forecast.\n"
            "\U0001F537 Помощь - /help.\n"
        )

    def _send_response(
        self, chat_id, text: str, sticker_id: str = None, keyboard=None,
        parse_mode=None, reply_to_message_id=None
    ):
        """
        Unified method to send a message and optionally a sticker.
        
        Args:
            chat_id: Telegram chat ID.
            text: Text message to send.
            sticker_id: Optional sticker ID.
            keyboard: Optional reply keyboard or inline keyboard.
            parse_mode: Optional parse mode (e.g., 'HTML').
            reply_to_message_id: Optional message ID to reply to.
        """
        send_action(self.bot, chat_id, 'typing')
        time.sleep(1)
        send_message(
            self.bot, chat_id, text,
            reply_markup=keyboard, parse_mode=parse_mode
        )
        if sticker_id:
            send_sticker(
                self.bot, chat_id, sticker_id,
                reply_to_message_id=reply_to_message_id,
                reply_markup=remove_keyboard() if keyboard is None else keyboard
            )

    def handle_weather_request(self, message: telebot.types.Message):
        """
        Handle incoming weather requests.

        Handles:
        - City name in Cyrillic (asks to use Latin characters)
        - Invalid input like '...'
        - Location-based requests
        - City-based requests
        - Service unavailability
        """
        username = get_username(message)

        if not self.weather.is_online():
            return self._send_service_unavailable(message, username)

        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help")
        )

        # Check for Cyrillic
        if message.text and re.search(r'[\u0400-\u04FF]', message.text):
            answer = f"{username.title()}, пожалуйста введите название города латиницей.\n" + self._help_text()
            return self._send_response(message.chat.id, answer, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA', keyboard)

        # Check for invalid input
        if message.text == '...':
            answer = f"<b>{message.text.capitalize()}</b> не найден!\n" + self._help_text()
            return self._send_response(message.chat.id, answer, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA', keyboard, parse_mode='HTML')

        # Get weather
        if message.location:
            weather_data = self.weather.get_current_weather(
                lat=message.location.latitude,
                lon=message.location.longitude
            )
        else:
            weather_data = self.weather.get_current_weather(city=message.text)

        # Location not found
        if not weather_data:
            city_name = message.text.capitalize() if message.text else "..."
            answer = f"<b>{city_name}</b> не найден!\n" + self._help_text()
            return self._send_response(message.chat.id, answer, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA', keyboard, parse_mode='HTML')

        # Send weather data
        answer = self.weather.format_current_weather(username.title(), weather_data)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode='HTML')

    def handle_wrong_content(self, message: telebot.types.Message):
        """
        Handle unsupported content types (e.g., images, files).

        Responds with a random sticker from WRONG_CONTENT_STICKERS.
        """
        self._send_response(
            message.chat.id,
            text="",
            sticker_id=random.choice(WRONG_CONTENT_STICKERS),
            reply_to_message_id=message.message_id
        )

    def _send_service_unavailable(self, message, username):
        """
        Notify the user that the weather service is currently unavailable.

        Args:
            message: Telegram message object.
            username: Username to personalize the message.
        """
        answer = f"{username}, прошу прощения, в данный момент сервис погоды не доступен!\nПопробуйте позже"
        self._send_response(message.chat.id, answer, random.choice(ERROR_STICKERS))
