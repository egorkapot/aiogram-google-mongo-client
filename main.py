import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.bot import bot
from bot.handlers.admin_delete_button import DeleteRouter
from bot.handlers.cmd_cancel import CancelRouter
from bot.handlers.cmd_me import MeRouter
from bot.handlers.cmd_start import RegistrationRouter
from bot.handlers.reply_button_handlers import ButtonHandlerRouter
from client.google_client.client import google_client
from client.mongo_client.client import mongo_client
from settings import settings

author_chat_id = settings.author_chat_id  # Chat id of creator for logging
dp = Dispatcher(storage=MemoryStorage())
cancel_router = CancelRouter()
me_router = MeRouter()
delete_router = DeleteRouter(bot, mongo_client, google_client, author_chat_id)
button_handler_router = ButtonHandlerRouter(
    bot, mongo_client, google_client, author_chat_id
)
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
        cancel_router, me_router, delete_router, button_handler_router, start_router
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
