"""Callback query handlers for inline buttons."""
import telebot
from utils.bot_helpers import create_inline_keyboard, create_location_keyboard
from handlers.base import BaseHandler
from handlers.shared import SharedResponses


class CallbackHandlers(BaseHandler):
    """Handlers for inline button callbacks."""
    
    def __init__(self, bot: telebot.TeleBot, command_handlers):
        """Initialize handlers with bot and command handlers."""
        super().__init__(bot)
        self.command_handlers = command_handlers
        self.shared = SharedResponses(bot)
    
    def handle_callback(self, callback: telebot.types.CallbackQuery) -> None:
        """Handle all callback queries."""
        if not callback.message:
            return
        
        username = self.get_username(callback)
        
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
        self.shared.send_help(callback.message.chat.id, username)
    
    def _handle_author_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle author button callback."""
        self.shared.send_author(callback.message.chat.id)
    
    def _handle_location_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle location button callback."""
        keyboard = create_location_keyboard()
        text = f"{username.title()}, нажмите на кнопку '\U0001F310 location' для отправки местоположения\n"
        self.send_response(callback.message.chat.id, text, reply_markup=keyboard)
    
    def _handle_forecast_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast button callback."""
        keyboard = create_location_keyboard()
        text = f"{username.title()}, введите город для получения прогноза на 5 дней или\n"
        text += "нажмите '\U0001F310 location' для отправки местоположения\n"
        self.send_response(callback.message.chat.id, text, reply_markup=keyboard)
        self.bot.register_next_step_handler(callback.message, self.command_handlers.handle_forecast_input)
    
    def _handle_forecast_help_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast help button callback."""
        keyboard = create_inline_keyboard(("author", "forecast_author"), row_width=1)
        text = f"{username.title()}, введите название города латиницей.\n"
        text += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
        text += "\U0001F537 Прогноз по местоположению - '\U0001F310 location'.\n"
        text += "\U0001F537 Информации об авторе - author.\n"
        self.send_response(callback.message.chat.id, text, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA', 
                          reply_markup=keyboard, parse_mode='HTML')
    
    def _handle_forecast_author_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast author button callback."""
        text = "\U0001F537 Author: <b>Yevhen Skyba</b>\n"
        text += "\U0001F537 Email: skiba.eugene@gmail.com\n"
        text += "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
        text += "\U0001F537 Telegram: @phobbii"
        self.send_response(callback.message.chat.id, text, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA', parse_mode='HTML')
