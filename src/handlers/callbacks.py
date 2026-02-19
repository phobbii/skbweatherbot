"""Callback query handlers for inline buttons."""
import telebot

from config import STICKER_HELP
from handlers.base import BaseHandler
from handlers.messages_text import (
    MSG_ENTER_CITY_OR_LOCATION,
    MSG_PRESS_LOCATION_BUTTON,
    get_forecast_help_message,
)
from utils.bot_helpers import create_inline_keyboard, create_location_keyboard


class CallbackHandlers(BaseHandler):
    """Handlers for inline button callbacks."""

    def __init__(self, bot: telebot.TeleBot, command_handlers) -> None:
        super().__init__(bot)
        self.command_handlers = command_handlers

    def handle_callback(self, callback: telebot.types.CallbackQuery) -> None:
        """Route callback query to the appropriate handler."""
        if not callback.message:
            return

        username = self.get_username(callback)
        chat_id = callback.message.chat.id

        handler = self._DISPATCH.get(callback.data)
        if handler:
            handler(self, chat_id, username, callback)

    def _on_help(self, chat_id: int, username: str, _cb: telebot.types.CallbackQuery) -> None:
        self.send_help(chat_id, username)

    def _on_author(self, chat_id: int, _username: str, _cb: telebot.types.CallbackQuery) -> None:
        self.send_author(chat_id)

    def _on_location(self, chat_id: int, username: str, _cb: telebot.types.CallbackQuery) -> None:
        self.send_response(
            chat_id,
            MSG_PRESS_LOCATION_BUTTON.format(username=username),
            reply_markup=create_location_keyboard(),
        )

    def _on_forecast(self, chat_id: int, username: str, cb: telebot.types.CallbackQuery) -> None:
        self.send_response(
            chat_id,
            MSG_ENTER_CITY_OR_LOCATION.format(username=username),
            reply_markup=create_location_keyboard(),
        )
        self.bot.register_next_step_handler(cb.message, self.command_handlers.handle_forecast_input)

    def _on_forecast_help(self, chat_id: int, username: str, _cb: telebot.types.CallbackQuery) -> None:
        keyboard = create_inline_keyboard(("author", "forecast_author"), row_width=1)
        self.send_response(
            chat_id,
            get_forecast_help_message(username),
            STICKER_HELP,
            reply_markup=keyboard,
            parse_mode="HTML",
        )

    def _on_forecast_author(self, chat_id: int, _username: str, _cb: telebot.types.CallbackQuery) -> None:
        self.send_author(chat_id)

    _DISPATCH = {
        "help": _on_help,
        "author": _on_author,
        "location": _on_location,
        "forecast": _on_forecast,
        "forecast_help": _on_forecast_help,
        "forecast_author": _on_forecast_author,
    }
