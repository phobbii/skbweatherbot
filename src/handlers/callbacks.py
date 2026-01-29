"""Callback query handlers for inline buttons."""
import telebot
from utils.bot_helpers import create_inline_keyboard, create_location_keyboard
from handlers.base import BaseHandler
from handlers.messages_text import (
    AUTHOR_INFO, STICKER_AUTHOR, STICKER_HELP, 
    MSG_PRESS_LOCATION_BUTTON, MSG_ENTER_CITY_OR_LOCATION,
    get_forecast_help_message
)


class CallbackHandlers(BaseHandler):
    """Handlers for inline button callbacks."""
    
    def __init__(self, bot: telebot.TeleBot, command_handlers):
        """Initialize handlers with bot and command handlers."""
        super().__init__(bot)
        self.command_handlers = command_handlers
    
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
        self.send_help(callback.message.chat.id, username)
    
    def _handle_author_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle author button callback."""
        self.send_author(callback.message.chat.id)
    
    def _handle_location_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle location button callback."""
        keyboard = create_location_keyboard()
        self.send_response(callback.message.chat.id, MSG_PRESS_LOCATION_BUTTON.format(username=username.title()), reply_markup=keyboard)
    
    def _handle_forecast_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast button callback."""
        keyboard = create_location_keyboard()
        self.send_response(callback.message.chat.id, MSG_ENTER_CITY_OR_LOCATION.format(username=username.title()), reply_markup=keyboard)
        self.bot.register_next_step_handler(callback.message, self.command_handlers.handle_forecast_input)
    
    def _handle_forecast_help_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast help button callback."""
        keyboard = create_inline_keyboard(("author", "forecast_author"), row_width=1)
        self.send_response(callback.message.chat.id, get_forecast_help_message(username.title()), STICKER_HELP, 
                          reply_markup=keyboard, parse_mode='HTML')
    
    def _handle_forecast_author_callback(self, callback: telebot.types.CallbackQuery, username: str) -> None:
        """Handle forecast author button callback."""
        self.send_response(callback.message.chat.id, AUTHOR_INFO, STICKER_AUTHOR, parse_mode='HTML')
