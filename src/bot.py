#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Main bot entry point."""
import ssl
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import telebot
from aiohttp import web

import config
from services.weather_service import WeatherService
from handlers.commands import CommandHandlers
from handlers.messages import MessageHandlers
from handlers.callbacks import CallbackHandlers

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize bot and services
bot = telebot.TeleBot(config.TELEBOT_KEY, threaded=False)
weather_service = WeatherService(config.OWM_KEY)

# Initialize handlers
cmd_handlers = CommandHandlers(bot, weather_service)
msg_handlers = MessageHandlers(bot, weather_service)
callback_handlers = CallbackHandlers(bot, cmd_handlers)

# Setup aiohttp app
app = web.Application()
executor = ThreadPoolExecutor(max_workers=4)


async def handle_webhook(request: web.Request) -> web.Response:
    """Handle incoming webhook requests."""
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            executor,
            bot.process_new_updates,
            [update]
        )
        return web.Response()
    return web.Response(status=403)

app.router.add_post('/{token}/', handle_webhook)


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


@bot.message_handler(func=lambda m: True, content_types=config.CONTENT_TO_HANDLE)
def weather_message(message: telebot.types.Message) -> None:
    msg_handlers.handle_weather_request(message)


@bot.message_handler(func=lambda m: True, content_types=config.CONTENT_TO_REJECT)
def wrong_content_message(message: telebot.types.Message) -> None:
    msg_handlers.handle_wrong_content(message)


def main() -> None:
    """Main function to start the bot."""
    logger.info("Starting bot...")

    # Setup webhook
    bot.remove_webhook()

    # Read certificate fully before set_webhook
    with open(config.WEBHOOK_SSL_CERT, 'rb') as f:
        cert_data = f.read()

    bot.set_webhook(
        url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
        certificate=cert_data
    )
    logger.info(f"Webhook set to {config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH}")

    # Setup SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)

    # Start server
    logger.info(f"Starting server on {config.WEBHOOK_LISTENER}:{config.WEBHOOK_PORT}")
    web.run_app(
        app,
        host=config.WEBHOOK_LISTENER,
        port=int(config.WEBHOOK_PORT),
        ssl_context=context
    )

if __name__ == '__main__':
    main()
