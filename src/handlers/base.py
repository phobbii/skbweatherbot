"""Base handler with common functionality."""
import time
import random
import telebot
from utils.bot_helpers import send_action, send_message, send_sticker, get_username
from config import ERROR_STICKERS


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
        text = f"{username}, прошу прощения, в данный момент сервис погоды не доступен!\nПопробуйте позже\n"
        self.send_response(chat_id, text, random.choice(ERROR_STICKERS), **kwargs)
    
    def send_city_not_found(self, chat_id: int, city_name: str, keyboard) -> None:
        """Send city not found message."""
        text = f"<b>{city_name}</b> не найден!\n"
        text += "\U0001F537 Прогноз по местоположению - /location.\n"
        text += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
        text += "\U0001F537 Помощь - /help.\n"
        self.send_response(chat_id, text, 'CAADAgADegIAAvnkbAABGyiSVUu1QfIWBA', 
                          reply_markup=keyboard, parse_mode='HTML')
    
    def send_cyrillic_error(self, chat_id: int, username: str, keyboard) -> None:
        """Send Cyrillic input error message."""
        text = f"{username.title()}, пожалуйста введите название города латиницей.\n"
        text += "\U0001F537 Прогноз по местоположению - /location.\n"
        text += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
        text += "\U0001F537 Помощь - /help.\n"
        self.send_response(chat_id, text, 'CAADAgADewIAAvnkbAABeDnKq9BHIbAWBA', 
                          reply_markup=keyboard)
    
    def get_username(self, message_or_callback) -> str:
        """Get username from message or callback."""
        return get_username(message_or_callback)
