"""Command handlers for the bot."""
import re
import telebot
from utils.bot_helpers import create_inline_keyboard, create_location_keyboard, remove_keyboard, reply_to_message
from services.weather_service import WeatherService
from handlers.base import BaseHandler
from handlers.messages_text import (
    STICKER_START, MSG_PRESS_LOCATION_BUTTON, MSG_ENTER_CITY_OR_LOCATION,
    get_start_message, get_forecast_cyrillic_error, get_forecast_city_not_found
)


class CommandHandlers(BaseHandler):
    """Handlers for bot commands."""
    
    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService):
        """Initialize handlers with bot and weather service."""
        super().__init__(bot)
        self.weather = weather_service
    
    def handle_start(self, message: telebot.types.Message) -> None:
        """Handle /start command."""
        username = self.get_username(message)
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help"),
            ("author", "author")
        )
        self.send_response(message.chat.id, get_start_message(username.title()), STICKER_START, reply_markup=keyboard)
    
    def handle_location(self, message: telebot.types.Message) -> None:
        """Handle /location command."""
        username = self.get_username(message)
        keyboard = create_location_keyboard()
        self.send_response(message.chat.id, MSG_PRESS_LOCATION_BUTTON.format(username=username.title()), reply_markup=keyboard)
    
    def handle_forecast_command(self, message: telebot.types.Message) -> None:
        """Handle /forecast command."""
        username = self.get_username(message)
        keyboard = create_location_keyboard()
        self.send_response(message.chat.id, MSG_ENTER_CITY_OR_LOCATION.format(username=username.title()), reply_markup=keyboard)
        self.bot.register_next_step_handler(message, self.handle_forecast_input)
    
    def handle_forecast_input(self, message: telebot.types.Message) -> None:
        """Handle forecast input (city or location)."""
        username = self.get_username(message)
        
        if not self.weather.is_online():
            self.send_service_unavailable(message.chat.id, username, reply_markup=remove_keyboard())
            return
        
        keyboard = create_inline_keyboard(("help", "forecast_help"))
        
        # Check for Cyrillic
        if message.text and re.search(r'[\u0400-\u04FF]', message.text):
            self.send_response(message.chat.id, get_forecast_cyrillic_error(username.title()), 
                             'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA', reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return
        
        # Get forecast
        if message.location:
            forecast_data = self.weather.get_forecast(lat=message.location.latitude, lon=message.location.longitude)
        else:
            forecast_data = self.weather.get_forecast(city=message.text)
        
        if not forecast_data:
            city_name = message.text.capitalize() if message.text else "..."
            self.send_response(message.chat.id, get_forecast_city_not_found(city_name), 
                             'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA', 
                             reply_markup=keyboard, parse_mode='HTML')
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return
        
        answer = self.weather.format_forecast(username.title(), forecast_data)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
    
    def handle_help(self, message: telebot.types.Message) -> None:
        """Handle /help command."""
        username = self.get_username(message)
        self.send_help(message.chat.id, username)
    
    def handle_author(self, message: telebot.types.Message) -> None:
        """Handle /author command."""
        self.send_author(message.chat.id)
