#!/usr/bin/env python
"""Main bot entry point."""
import logging

from typing import Any

import functions_framework
import telebot

import config
from handlers.callbacks import CallbackHandlers
from handlers.commands import CommandHandlers
from handlers.messages import MessageHandlers
from services.weather_service import WeatherService


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Initialize bot and services
bot = telebot.TeleBot(config.TELEBOT_KEY, threaded=False)
weather_service = WeatherService(config.OWM_KEY)

# Initialize handlers
cmd_handlers = CommandHandlers(bot, weather_service)
msg_handlers = MessageHandlers(bot, weather_service)
callback_handlers = CallbackHandlers(bot, cmd_handlers)


def is_private_or_mentioned(message: telebot.types.Message) -> bool:
    """In private chats allow all messages; in groups only if bot is mentioned or replied to."""
    if message.chat.type == 'private':
        return True
    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.username == config.BOT_USERNAME:
        return True
    if message.text and f'@{config.BOT_USERNAME}' in message.text:
        return True
    return False


# Register handlers
@bot.message_handler(commands=['start'])
def start_command(message: telebot.types.Message) -> None:
    cmd_handlers.handle_start(message)


@bot.message_handler(commands=['location'])
def location_command(message: telebot.types.Message) -> None:
    cmd_handlers.handle_location(message)


@bot.message_handler(commands=['forecast'], content_types=config.CONTENT_TO_HANDLE)
def forecast_command(message: telebot.types.Message) -> None:
    cmd_handlers.handle_forecast_command(message)


@bot.message_handler(commands=['help'])
def help_command(message: telebot.types.Message) -> None:
    cmd_handlers.handle_help(message)


@bot.message_handler(commands=['author'])
def author_command(message: telebot.types.Message) -> None:
    cmd_handlers.handle_author(message)


@bot.callback_query_handler(func=lambda c: True)
def callback_query(callback: telebot.types.CallbackQuery) -> None:
    callback_handlers.handle_callback(callback)


@bot.message_handler(func=is_private_or_mentioned, content_types=config.CONTENT_TO_HANDLE)
def weather_message(message: telebot.types.Message) -> None:
    if message.text:
        message.text = message.text.replace(f'@{config.BOT_USERNAME}', '').strip()
    msg_handlers.handle_weather_request(message)


@bot.message_handler(func=is_private_or_mentioned, content_types=config.CONTENT_TO_REJECT)
def wrong_content_message(message: telebot.types.Message) -> None:
    msg_handlers.handle_wrong_content(message)


@functions_framework.http
def webhook_run(request: Any) -> tuple[str, int]:
    """Handle incoming Telegram webhook requests."""
    if request.method != 'POST':
        logger.warning('Non-POST request received')
        return 'Method Not Allowed', 405

    token = request.headers.get('X-Telegram-Bot-Api-Secret-Token')
    if token != config.WEBHOOK_TOKEN:
        logger.warning('Invalid secret token')
        return 'Forbidden', 403

    try:
        body = request.get_json(silent=True)
        if not body:
            logger.warning('Empty request body')
            return 'Bad Request', 400

        update = telebot.types.Update.de_json(body)
        logger.info(
            f'Update received: id={update.update_id}, '
            f'type={"message" if update.message else "callback" if update.callback_query else "other"}'
        )
        bot.process_new_updates([update])
    except Exception:
        logger.exception('Error processing update')

    return 'OK', 200


def local_run() -> None:
    """Local long polling."""
    logger.info('Starting bot in local polling mode...')
    try:
        bot.remove_webhook()
        logger.info('Webhook removed. Starting infinity polling.')
        bot.infinity_polling(timeout=100, long_polling_timeout=100)
    except Exception:
        logger.exception('Bot stopped due to an unexpected error in local polling')


if __name__ == '__main__':
    local_run()
