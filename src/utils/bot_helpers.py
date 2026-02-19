"""Utility functions for bot operations."""
import logging
import time
from datetime import date as date_type
from typing import Any, Callable, Optional, Union

import emoji
import telebot
from babel.dates import format_date

logger = logging.getLogger(__name__)

MessageOrCallback = Union[telebot.types.Message, telebot.types.CallbackQuery]


def send_with_retry(func: Callable, *args, max_retries: int = 5, delay: int = 5, **kwargs) -> Any:
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


def _filter_kwargs(**kwargs) -> dict[str, Any]:
    """Return only non-None keyword arguments."""
    return {k: v for k, v in kwargs.items() if v is not None}


def send_action(bot: telebot.TeleBot, chat_id: int, action: str) -> None:
    """Send chat action with retry."""
    send_with_retry(bot.send_chat_action, chat_id, action)


def send_message(
    bot: telebot.TeleBot,
    chat_id: int,
    text: str,
    reply_markup: Optional[Any] = None,
    parse_mode: Optional[str] = None,
) -> None:
    """Send message with retry."""
    send_with_retry(bot.send_message, chat_id, text, **_filter_kwargs(reply_markup=reply_markup, parse_mode=parse_mode))


def reply_to_message(
    bot: telebot.TeleBot,
    message: telebot.types.Message,
    text: str,
    reply_markup: Optional[Any] = None,
    parse_mode: Optional[str] = None,
) -> None:
    """Reply to message with retry."""
    send_with_retry(bot.reply_to, message, text, **_filter_kwargs(reply_markup=reply_markup, parse_mode=parse_mode))


def send_sticker(
    bot: telebot.TeleBot,
    chat_id: int,
    sticker: str,
    reply_to_message_id: Optional[int] = None,
    reply_markup: Optional[Any] = None,
) -> None:
    """Send sticker with retry."""
    send_with_retry(
        bot.send_sticker, chat_id, sticker,
        **_filter_kwargs(reply_to_message_id=reply_to_message_id, reply_markup=reply_markup),
    )


def get_username(source: MessageOrCallback) -> str:
    """Extract username from message or callback query."""
    return source.from_user.first_name or source.from_user.username


def create_inline_keyboard(*buttons: tuple[str, str], row_width: int = 2) -> telebot.types.InlineKeyboardMarkup:
    """Create inline keyboard from button tuples (text, callback_data)."""
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=row_width)
    keyboard.add(*(
        telebot.types.InlineKeyboardButton(text=text, callback_data=data)
        for text, data in buttons
    ))
    return keyboard


def create_location_keyboard() -> telebot.types.ReplyKeyboardMarkup:
    """Create keyboard with location request button."""
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(telebot.types.KeyboardButton(text="\U0001F310 location", request_location=True))
    return keyboard


def remove_keyboard() -> telebot.types.ReplyKeyboardRemove:
    """Create keyboard removal markup."""
    return telebot.types.ReplyKeyboardRemove(selective=False)


def is_emoji(text: str) -> bool:
    """Check if text contains any emoji."""
    if not text:
        return False
    return bool(emoji.emoji_list(text))


def format_localized_weekday(day: date_type, locale: str) -> str:
    """Return a localized full weekday and date string, mapping 'ua' to 'uk' for babel."""
    babel_locale = 'uk' if locale.lower() == 'ua' else locale.lower()
    return format_date(day, 'EEEE, d MMMM y', locale=babel_locale)
