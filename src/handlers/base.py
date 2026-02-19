"""Base handler with common functionality."""
import logging
import random
import time
from typing import Optional, Union

import telebot

from config import ERROR_STICKERS
from handlers.messages_text import (
    AUTHOR_INFO,
    MSG_SERVICE_UNAVAILABLE,
    STICKER_AUTHOR,
    STICKER_CITY_NOT_FOUND,
    STICKER_HELP,
    get_city_not_found_message,
    get_help_message,
)
from utils.bot_helpers import (
    create_inline_keyboard,
    get_username,
    remove_keyboard,
    send_action,
    send_message,
    send_sticker,
)

logger = logging.getLogger(__name__)

MessageOrCallback = Union[telebot.types.Message, telebot.types.CallbackQuery]


class BaseHandler:
    """Base handler with common response methods."""

    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot

    @staticmethod
    def get_username(source: MessageOrCallback) -> str:
        """Extract display name from message or callback, title-cased."""
        return get_username(source).title()

    def send_response(
        self,
        chat_id: int,
        text: str,
        sticker_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Send typing action, message, and optional sticker."""
        send_action(self.bot, chat_id, "typing")
        time.sleep(1)
        send_message(self.bot, chat_id, text, **kwargs)
        if sticker_id:
            send_sticker(self.bot, chat_id, sticker_id)

    def send_service_unavailable(self, chat_id: int, username: str, **kwargs) -> None:
        """Send service unavailable error with a random error sticker."""
        self.send_response(
            chat_id,
            MSG_SERVICE_UNAVAILABLE.format(username=username),
            random.choice(ERROR_STICKERS),
            **kwargs,
        )

    def send_city_not_found(
        self,
        chat_id: int,
        city_name: str,
        keyboard,
        instructions: tuple[str, ...] = (),
    ) -> None:
        """Send city-not-found message with configurable instructions."""
        self.send_response(
            chat_id,
            get_city_not_found_message(city_name, instructions),
            STICKER_CITY_NOT_FOUND,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    def send_help(self, chat_id: int, username: str) -> None:
        """Send help message with inline navigation."""
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("author", "author"),
        )
        self.send_response(
            chat_id,
            get_help_message(username),
            STICKER_HELP,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    def send_author(self, chat_id: int) -> None:
        """Send author information."""
        self.send_response(
            chat_id,
            AUTHOR_INFO,
            STICKER_AUTHOR,
            reply_markup=remove_keyboard(),
            parse_mode="HTML",
        )
