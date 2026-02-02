"""Command handlers for the bot."""
import re
import telebot
from utils.bot_helpers import create_inline_keyboard, create_location_keyboard, remove_keyboard, reply_to_message
from services.weather_service import WeatherService
from handlers.base import BaseHandler
from handlers.shared import SharedResponses


class CommandHandlers(BaseHandler):
    """Handlers for bot commands."""
    
    def __init__(self, bot: telebot.TeleBot, weather_service: WeatherService):
        """Initialize handlers with bot and weather service."""
        super().__init__(bot)
        self.weather = weather_service
        self.shared = SharedResponses(bot)
    
    def handle_start(self, message: telebot.types.Message) -> None:
        """Handle /start command."""
        username = self.get_username(message)
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("help", "help"),
            ("author", "author")
        )
        text = f"Привет {username.title()}.\n"
        text += "\U0001F537 Введите город латиницей для получения погоды или\n"
        text += "отправьте текущее местоположение - /location.\n"
        text += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
        text += "\U0001F537 Помощь - /help.\n"
        text += "\U0001F537 Информации об авторе - /author.\n"
        self.send_response(message.chat.id, text, 'CAADAgADfQIAAvnkbAABcAABA648YQ08FgQ', reply_markup=keyboard)
    
    def handle_location(self, message: telebot.types.Message) -> None:
        """Handle /location command."""
        username = self.get_username(message)
        keyboard = create_location_keyboard()
        text = f"{username.title()}, нажмите на кнопку '\U0001F310 location' для отправки местоположения\n"
        self.send_response(message.chat.id, text, reply_markup=keyboard)
    
    def handle_forecast_command(self, message: telebot.types.Message) -> None:
        """Handle /forecast command."""
        username = self.get_username(message)
        keyboard = create_location_keyboard()
        text = f"{username.title()}, введите город для получения прогноза на 5 дней или\n"
        text += "нажмите '\U0001F310 location' для отправки местоположения\n"
        self.send_response(message.chat.id, text, reply_markup=keyboard)
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
            text = f"{username.title()}, пожалуйста введите название города латиницей.\n"
            text += "\U0001F537 Прогноз по местоположению - '\U0001F310 location'.\n"
            text += "\U0001F537 Помощь - help.\n"
            self.send_response(message.chat.id, text, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA', reply_markup=keyboard)
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return
        
        # Get forecast
        if message.location:
            forecast_data = self.weather.get_forecast(lat=message.location.latitude, lon=message.location.longitude)
        else:
            forecast_data = self.weather.get_forecast(city=message.text)
        
        if not forecast_data:
            city_name = message.text.capitalize() if message.text else "..."
            text = f"<b>{city_name}</b> не найден!\n"
            text += "\U0001F537 Прогноз по местоположению - '\U0001F310 location'.\n"
            text += "\U0001F537 Помощь - help.\n"
            self.send_response(message.chat.id, text, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA', 
                             reply_markup=keyboard, parse_mode='HTML')
            self.bot.register_next_step_handler(message, self.handle_forecast_input)
            return
        
        answer = self.weather.format_forecast(username.title(), forecast_data)
        reply_to_message(self.bot, message, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
    
    def handle_help(self, message: telebot.types.Message) -> None:
        """Handle /help command."""
        username = self.get_username(message)
        self.shared.send_help(message.chat.id, username)
    
    def handle_author(self, message: telebot.types.Message) -> None:
        """Handle /author command."""
        self.shared.send_author(message.chat.id)
