"""Utility functions for bot operations."""
import time
import logging
from typing import Any, Optional
import telebot

logger = logging.getLogger(__name__)


def send_with_retry(func, *args, max_retries: int = 5, delay: int = 5, **kwargs) -> Any:
    """Generic retry wrapper for bot API calls."""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{e} - Retry {attempt + 1}/{max_retries} after {delay}s")
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                raise


def send_action(bot: telebot.TeleBot, chat_id: int, action: str) -> None:
    """Send chat action with retry."""
    send_with_retry(bot.send_chat_action, chat_id, action)


def send_message(bot: telebot.TeleBot, chat_id: int, text: str, 
                reply_markup: Optional[Any] = None, parse_mode: Optional[str] = None) -> None:
    """Send message with retry."""
    kwargs = {}
    if reply_markup:
        kwargs['reply_markup'] = reply_markup
    if parse_mode:
        kwargs['parse_mode'] = parse_mode
    send_with_retry(bot.send_message, chat_id, text, **kwargs)


def reply_to_message(bot: telebot.TeleBot, message: telebot.types.Message, text: str,
                    reply_markup: Optional[Any] = None, parse_mode: Optional[str] = None) -> None:
    """Reply to message with retry."""
    kwargs = {}
    if reply_markup:
        kwargs['reply_markup'] = reply_markup
    if parse_mode:
        kwargs['parse_mode'] = parse_mode
    send_with_retry(bot.reply_to, message, text, **kwargs)


def send_sticker(bot: telebot.TeleBot, chat_id: int, sticker: str,
                reply_to_message_id: Optional[int] = None, 
                reply_markup: Optional[Any] = None) -> None:
    """Send sticker with retry."""
    kwargs = {}
    if reply_to_message_id:
        kwargs['reply_to_message_id'] = reply_to_message_id
    if reply_markup:
        kwargs['reply_markup'] = reply_markup
    send_with_retry(bot.send_sticker, chat_id, sticker, **kwargs)


def get_username(message: telebot.types.Message) -> str:
    """Extract username from message."""
    return message.from_user.first_name or message.from_user.username


def create_inline_keyboard(*buttons: tuple[str, str], row_width: int = 2) -> telebot.types.InlineKeyboardMarkup:
    """Create inline keyboard from button tuples (text, callback_data)."""
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=row_width)
    btn_objects = [telebot.types.InlineKeyboardButton(text=text, callback_data=data) 
                   for text, data in buttons]
    keyboard.add(*btn_objects)
    return keyboard


def create_location_keyboard() -> telebot.types.ReplyKeyboardMarkup:
    """Create keyboard with location request button."""
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    location_btn = telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True)
    keyboard.add(location_btn)
    return keyboard


def remove_keyboard() -> telebot.types.ReplyKeyboardRemove:
    """Create keyboard removal markup."""
    return telebot.types.ReplyKeyboardRemove(selective=False)
