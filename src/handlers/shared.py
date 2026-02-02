"""Shared response handlers."""
import telebot
from utils.bot_helpers import create_inline_keyboard, remove_keyboard
from handlers.base import BaseHandler


class SharedResponses(BaseHandler):
    """Common response handlers used across modules."""
    
    def send_help(self, chat_id: int, username: str) -> None:
        """Send help message."""
        keyboard = create_inline_keyboard(
            ("location", "location"),
            ("forecast", "forecast"),
            ("author", "author")
        )
        text = f"{username.title()}, введите название города латиницей.\n"
        text += "\U0001F537 Пример: <b>Kharkiv</b>.\n"
        text += "\U0001F537 Прогноз по местоположению - /location.\n"
        text += "\U0001F537 Прогноз на 5 дней - /forecast.\n"
        text += "\U0001F537 Информации об авторе - /author.\n"
        self.send_response(chat_id, text, 'CAADAgADxwIAAvnkbAABx601cOaIcf8WBA', 
                          reply_markup=keyboard, parse_mode='HTML')
    
    def send_author(self, chat_id: int) -> None:
        """Send author information."""
        text = "\U0001F537 Author: <b>Yevhen Skyba</b>\n"
        text += "\U0001F537 Email: skiba.eugene@gmail.com\n"
        text += "\U0001F537 LinkedIn: https://www.linkedin.com/in/yevhen-skyba/\n"
        text += "\U0001F537 Telegram: @phobbii"
        self.send_response(chat_id, text, 'CAADAgADtQEAAvnkbAABxHAP4NXF1FcWBA', 
                          reply_markup=remove_keyboard(), parse_mode='HTML')
