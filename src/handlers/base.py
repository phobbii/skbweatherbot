"""Base handler with common functionality."""
import time
import random
import telebot
from utils.bot_helpers import send_action, send_message, send_sticker, get_username, create_inline_keyboard, remove_keyboard
from config import ERROR_STICKERS
from handlers.messages_text import (
    MSG_SERVICE_UNAVAILABLE, STICKER_CITY_NOT_FOUND, STICKER_CYRILLIC_ERROR,
    AUTHOR_INFO, STICKER_AUTHOR, STICKER_HELP,
    get_city_not_found_message, get_cyrillic_error_message, get_help_message
)


class BaseHandler:
    """Base handler with common methods."""
    
    def __init__(self, bot: telebot.TeleBot):
        """Initialize with bot instance."""
        self.bot = bot
    
    def send_response(self, chat_id: int, text: str, sticker_id: str = None, **kwargs) -> None:
        """Send response with typing action and optional sticker."""
        send_action(self.bot, chat_id, 'typing')
        time.sleep(1)
        send_message(self.bot, chat_id, text, **kwargs)
        if sticker_id:
            send_sticker(self.bot, chat_id, sticker_id)
    
    def send_service_unavailable(self, chat_id: int, username: str, **kwargs) -> None:
        """Send service unavailable message."""
        self.send_response(chat_id, MSG_SERVICE_UNAVAILABLE.format(username=username), 
                          random.choice(ERROR_STICKERS), **kwargs)
    
    def send_city_not_found(self, chat_id: int, city_name: str, keyboard) -> None:
        """Send city not found message."""
        self.send_response(chat_id, get_city_not_found_message(city_name), STICKER_CITY_NOT_FOUND, 
                          reply_markup=keyboard, parse_mode='HTML')
    
    def send_cyrillic_error(self, chat_id: int, username: str, keyboard) -> None:
        """Send Cyrillic input error message."""
        self.send_response(chat_id, get_cyrillic_error_message(username.title()), STICKER_CYRILLIC_ERROR, 
                          reply_markup=keyboard)
    
    def send_help(self, chat_id: int, username: str) -> None:
        """Send help message."""
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("author", "author")
        )
        self.send_response(chat_id, get_help_message(username.title()), STICKER_HELP, 
                          reply_markup=keyboard, parse_mode='HTML')
    
    def send_author(self, chat_id: int) -> None:
        """Send author information."""
        self.send_response(chat_id, AUTHOR_INFO, STICKER_AUTHOR, 
                          reply_markup=remove_keyboard(), parse_mode='HTML')
    
    def get_username(self, message_or_callback) -> str:
        """Get username from message or callback."""
        return get_username(message_or_callback)
