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
from google_access_share_bot.google_client.utils import (is_google_document,
                                                 is_google_spreadsheet)
from google_access_share_bot.handlers.cmd_start import RegistrationRouter
from google_access_share_bot.handlers.cmd_cancel import CancelRouter
from google_access_share_bot.handlers.cmd_me import MeRouter
from google_access_share_bot.handlers.cmd_delete import DeleteRouter

settings = Settings()
bot_token = settings.get_bot_token().get_secret_value()
author_chat_id = settings.author_chat_id  # Chat id of creator for logging
bot = Bot(bot_token)
dp = Dispatcher(storage=MemoryStorage())
google_client = GoogleClient(bot, author_chat_id)
MONGO_HOST = settings.mongo_host
MONGO_PORT = settings.mongo_port
mongo_client = MongoUsersClient(bot, author_chat_id, MONGO_HOST, MONGO_PORT, 'db')
start_router = RegistrationRouter(bot, mongo_client, author_chat_id)
cancel_router = CancelRouter()
me_router = MeRouter()
delete_router = DeleteRouter(bot, mongo_client, google_client)


async def main() -> None:
    """
    Includes all routers and start the application.
    Important thing is to import the global routers before state-specific.
    This ensures that when a user enters a global command, it's processed correctly
    regardless of the FSM state they're in
    :return: None
    """
    dp.include_routers(
        cancel_router, delete_router, me_router, start_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



