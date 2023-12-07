import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from google_access_share_bot.bot.bot_package.buttons import inline_buttons
from google_access_share_bot.client.google_client.client import (
    GoogleClient, GoogleClientException)
from google_access_share_bot.client.mongo_client.client import MongoUsersClient
from google_access_share_bot.settings import settings
from google_access_share_bot.utils.utils import setup_logger


class CleanTableStates(StatesGroup):
    choosing_table_to_clean = State()


class CleanTableRouter(Router):
    def __init__(
        self,
        bot: Bot,
        mongo_client: MongoUsersClient,
        google_client: GoogleClient,
        log_chat_id: str,
    ):
        """
        Initialisation of the Mongo client, bot instance to handle bot-specific
        functions that are not supported by methods of Message class.

        :param bot: Instance of telebot
        :param mongo_client: Instance of Mongo database
        """
        super().__init__()
        self.bot = bot
        self.mongo_client = mongo_client
        self.google_client = google_client
        self.log_chat_id = log_chat_id
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger, self.bot, self.log_chat_id)
        self.message.register(self.handle_clean_table_button, F.text == "Clean Table")

    async def handle_clean_table_button(
        self, message: Message, state: FSMContext
    ) -> None:
        """
        Validates that the user is admin. Asks to provide table to clean

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        await state.clear()
        user_id_ = message.from_user.id
        try:
            user_role_ = self.mongo_client.get_user_data(user_id_).get("role")
        except AttributeError as e:
            await message.answer(f"You are not registered user!")
            return
        if user_role_ == "admin":
            await message.answer(
                "Please choose a table to clean",
                reply_markup=inline_buttons.generate_markup(
                    [
                        inline_buttons.working_tables_markup,
                        [inline_buttons.confirm_button, inline_buttons.skip_button],
                    ]
                ),
            )
            await state.set_state(CleanTableStates.choosing_table_to_clean)
        else:
            await message.answer("Prohibited to use admin commands")
