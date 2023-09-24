import logging
import os
from settings import Settings
from aiogram import F, Router
from aiogram.filters import Command
from googleapiclient.errors import HttpError
import asyncio
from aiogram.types import Message
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from google_access_share_bot.bot_logging.user_logging import \
    BotUserLoggingHandler
from google_access_share_bot.bot_package.buttons import *
from google_access_share_bot.google_client.client import GoogleClient
from google_access_share_bot.mongo_client.client import MongoUsersClient
from google_access_share_bot.utils.utils import (is_google_document,
                                                 is_google_spreadsheet)
from google_access_share_bot.handlers.registration import RegistrationRouter
settings = Settings()
bot_token = settings.get_bot_token().get_secret_value()
author_chat_id = settings.author_chat_id  # Chat id of creator for logging
admin_chat_id = settings.admin_chat_id
bot = Bot(bot_token)
dp = Dispatcher(storage=MemoryStorage())
google_client = GoogleClient(bot, admin_chat_id)
MONGO_HOST = settings.mongo_host
MONGO_PORT = settings.mongo_port
mongo_client = MongoUsersClient(bot, author_chat_id, MONGO_HOST, MONGO_PORT, 'db')
registration_router = RegistrationRouter(bot, mongo_client, author_chat_id)
me_router = Router()


async def main() -> None:
    dp.include_routers(me_router, registration_router)
    await dp.start_polling(bot)


@me_router.message(Command("me"))
async def me_command(message: Message):
    """Get user information"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    # Construct the message to send back to the user
    response = f"User ID: {user_id}\n"
    response += f"First Name: {first_name}\n"
    response += f"Last Name: {last_name}\n"
    response += f"Username: @{username}"
    await message.answer(response)

if __name__ == "__main__":
    asyncio.run(main())



