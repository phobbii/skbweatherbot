"""Callback query handlers for inline buttons."""
import time
import telebot
from utils.bot_helpers import (
    send_action, send_message, send_sticker, get_username,
    create_inline_keyboard, create_location_keyboard
)


class CallbackHandlers:
    """Handlers for inline button callbacks."""
    
    def __init__(self, bot: telebot.TeleBot):
        """Initialize handlers with bot."""
        self.bot = bot
    
    def handle_callback(self, callback: telebot.types.CallbackQuery) -> None:
        """Handle all callback queries."""
        if not callback.message:
            return
        
        username = get_username(callback)
        
        handlers = {
            'help': self._handle_help_callback,
            'author': self._handle_author_callback,
            'location': self._handle_location_callback,
            'forecast': self._handle_forecast_callback,
            'forecast_help': self._handle_forecast_help_callback,
            'forecast_author': self._handle_forecast_author_callback
        }
        
        handler = handlers.get(callback.data)
        if handler:
            handler(callback, username)
    
    def _handle_help_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle help button callback."""
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("author", "author")
        )
        
        answer = f"{username.title()}, введите название города латиницей.\n"
        answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
        answer += "\U0001F537 Прогноз погоды по местоположению - /location.\n"
        answer += "\U0001F537 Прогноз на 3 дня - /forecast.\n"
        answer += "\U0001F537 Информации об авторе - /author.\n"
        
        send_action(self.bot, callback.message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, callback.message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
        send_sticker(self.bot, callback.message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')
    
    def _handle_author_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle author button callback."""
        answer = "\U0001F537 Author: <b>Yevhen Skyba</b>\n"
        answer += "\U0001F537 Email: skiba.eugene@gmail.com\n"
        answer += "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
        answer += "\U0001F537 Telegram: @phobbii"
        
        send_action(self.bot, callback.message.chat.id, 'typing')
        time.sleep(1)
        from utils.bot_helpers import remove_keyboard
        send_message(self.bot, callback.message.chat.id, answer, reply_markup=remove_keyboard(), parse_mode='HTML')
        send_sticker(self.bot, callback.message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')
    
    def _handle_location_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle location button callback."""
        keyboard = create_location_keyboard()
        answer = f"{username.title()}, нажмите на кнопку '\U0001F310 location' для отправки местоположения\n"
        
        send_action(self.bot, callback.message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, callback.message.chat.id, answer, reply_markup=keyboard)
    
    def _handle_forecast_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast button callback."""
        keyboard = create_location_keyboard()
        answer = f"{username.title()}, введите город для получения прогноза на 3 дня или\n"
        answer += "нажмите '\U0001F310 location' для отправки местоположения\n"
        
        send_action(self.bot, callback.message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, callback.message.chat.id, answer, reply_markup=keyboard)
        
        # Import here to avoid circular dependency
        from handlers.commands import CommandHandlers
        from services.weather_service import WeatherService
        from config import OWM_KEY
        
        weather_service = WeatherService(OWM_KEY)
        cmd_handlers = CommandHandlers(self.bot, weather_service)
        self.bot.register_next_step_handler(callback.message, cmd_handlers.handle_forecast_input)
    
    def _handle_forecast_help_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast help button callback."""
        keyboard = create_inline_keyboard(("author", "forecast_author"), row_width=1)
        
        answer = f"{username.title()}, введите название города латиницей.\n"
        answer += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
        answer += "\U0001F537 Прогноз погоды по местоположению - '\U0001F310 location'.\n"
        answer += "\U0001F537 Информации об авторе - author.\n"
        
        send_action(self.bot, callback.message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, callback.message.chat.id, answer, reply_markup=keyboard, parse_mode='HTML')
        send_sticker(self.bot, callback.message.chat.id, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA')
    
    def _handle_forecast_author_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast author button callback."""
        answer = "\U0001F537 Author: <b>Yevhen Skyba</b>\n"
        answer += "\U0001F537 Email: skiba.eugene@gmail.com\n"
        answer += "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
        answer += "\U0001F537 Telegram: @phobbii"
        
        send_action(self.bot, callback.message.chat.id, 'typing')
        time.sleep(1)
        send_message(self.bot, callback.message.chat.id, answer, parse_mode='HTML')
        send_sticker(self.bot, callback.message.chat.id, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA')
