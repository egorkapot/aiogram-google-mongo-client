import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from google_access_share_bot.client.google_client.client import google_client

from google_access_share_bot.bot.handlers.cmd_cancel import CancelRouter
from google_access_share_bot.bot.handlers.admin_delete_button import DeleteRouter
from google_access_share_bot.bot.handlers.cmd_me import MeRouter
from google_access_share_bot.bot.handlers.cmd_start import RegistrationRouter
from google_access_share_bot.client.mongo_client.client import mongo_client
from google_access_share_bot.bot.bot import bot
from google_access_share_bot.bot.handlers.reply_button_handlers import ButtonHandlerRouter
from settings import settings

author_chat_id = settings.author_chat_id  # Chat id of creator for logging
dp = Dispatcher(storage=MemoryStorage())
cancel_router = CancelRouter()
me_router = MeRouter()
delete_router = DeleteRouter(bot, mongo_client, google_client, author_chat_id)
button_handler_router = ButtonHandlerRouter(bot, mongo_client, google_client, author_chat_id)
start_router = RegistrationRouter(bot, mongo_client, author_chat_id)


async def main() -> None:
    """
    Includes all routers and start the application.
    Important thing is to import the global routers before state-specific.
    This ensures that when a user enters a global command, it's processed correctly
    regardless of the FSM state they're in
    :return: None
    """
    dp.include_routers(
        cancel_router,
        me_router,
        delete_router,
        button_handler_router,
        start_router
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
