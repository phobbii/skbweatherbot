"""Command handlers for the bot."""
import telebot

from config import STICKER_START
from handlers.base import BaseHandler
from handlers.messages_text import (
    INSTRUCTION_HELP_BUTTON,
    INSTRUCTION_LOCATION_BUTTON,
    MSG_ENTER_CITY_OR_LOCATION,
    MSG_PRESS_LOCATION_BUTTON,
    get_start_message,
)
from services.weather_service import WeatherService
from utils.bot_helpers import (
    create_inline_keyboard,
    create_location_keyboard,
    remove_keyboard,
    reply_to_message,
)


class CommandHandlers(BaseHandler):
    """Handlers for bot commands."""

    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService) -> None:
        super().__init__(bot)
        self.weather = weather_service

    def handle_start(self, message: telebot.types.Message) -> None:
        """Handle /start command."""
        username = self.get_username(message)
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help"),
            ("author", "author"),
        )
        self.send_response(
            message.chat.id, get_start_message(username), STICKER_START, reply_markup=keyboard,
        )

    def handle_location(self, message: telebot.types.Message) -> None:
        """Handle /location command."""
        username = self.get_username(message)
        self.send_response(
            message.chat.id,
            MSG_PRESS_LOCATION_BUTTON.format(username=username),
            reply_markup=create_location_keyboard(),
        )

    def handle_forecast_command(self, message: telebot.types.Message) -> None:
        """Handle /forecast command — prompt user then wait for input."""
        username = self.get_username(message)
        self.send_response(
            message.chat.id,
            MSG_ENTER_CITY_OR_LOCATION.format(username=username),
            reply_markup=create_location_keyboard(),
        )
        self.bot.register_next_step_handler(message, self.handle_forecast_input)

    def handle_forecast_input(self, message: telebot.types.Message) -> None:
        """Handle forecast input (city name or shared location)."""
        username = self.get_username(message)
        keyboard = create_inline_keyboard(("help", "forecast_help"))

        if message.location:
            forecast_data = self.weather.get_forecast(lat=message.location.latitude, lon=message.location.longitude)
        else:
            forecast_data = self.weather.get_forecast(city=message.text)

        if not forecast_data:
            city_name = message.text.capitalize() if message.text else "..."
            self.send_city_not_found(
                message.chat.id, city_name, keyboard,
                instructions=(INSTRUCTION_LOCATION_BUTTON, INSTRUCTION_HELP_BUTTON),
            )
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return

        answer = self.weather.format_forecast(username, forecast_data)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode="HTML")

    def handle_help(self, message: telebot.types.Message) -> None:
        """Handle /help command."""
        self.send_help(message.chat.id, self.get_username(message))

    def handle_author(self, message: telebot.types.Message) -> None:
        """Handle /author command."""
        self.send_author(message.chat.id)
