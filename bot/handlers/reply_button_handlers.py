from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
import logging
from google_access_share_bot.bot.bot_package.buttons import (inline_buttons)
from google_access_share_bot.client.mongo_client.client import MongoUsersClient
from google_access_share_bot.client.google_client.client import GoogleClient, GoogleClientException
from google_access_share_bot.settings import settings
from google_access_share_bot.utils.utils import setup_logger


class ButtonHandlerStates(StatesGroup):
    clicked_all_links = State()
    clicked_open_access = State()


class ButtonHandlerRouter(Router):
    def __init__(
            self, bot: Bot, mongo_client: MongoUsersClient, google_client: GoogleClient, log_chat_id: str
    ):
        super().__init__()
        self.bot = bot
        self.google_client = google_client
        self.mongo_client = mongo_client
        self.log_chat_id = log_chat_id
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger, self.bot, self.log_chat_id)
        self.message.register(
            self.handle_all_links_reply_button,
            F.text == "All Links"
        )
        self.callback_query.register(
            self.handle_all_links_inline_button,
            ButtonHandlerStates.clicked_all_links,
            F.data.startswith("table_")
        )
        self.message.register(
            self.handle_open_the_access_button,
            F.text == "Open the access"
        )
        self.message.register(
            self.open_access,
            ButtonHandlerStates.clicked_open_access
        )

    async def handle_all_links_reply_button(self, message: Message, state: FSMContext) -> None:
        """
        Generates Inline Keyboard Markup depending on user role

        :param message: Message from user. In this case it is a click on 'All links' button
        :param state: Current state of user
        :return: None
        """
        user_id = message.from_user.id
        user_role = self.mongo_client.get_user_data(user_id).get("role")
        await message.answer(
            f"Please see the list of available links",
            reply_markup=inline_buttons.generate_all_link_markup(user_role)
        )
        await state.set_state(ButtonHandlerStates.clicked_all_links)

    @staticmethod
    async def handle_all_links_inline_button(call: CallbackQuery) -> None:
        """
        Retrieves the table name from callback and sends it to user with the  appropriate link

        :param call: Call from markup
        :return: None
        """
        table_name = call.data.split("table_")[1]
        link_to_table = settings.get_table_link(table_name)
        await call.message.answer(f"Link for {table_name}: {link_to_table}")

    async def handle_open_the_access_button(self, message: Message, state: FSMContext) -> None:
        """
        Triggers when user clicked open access function.
        Asks user to provide links to open access.

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        await message.answer(
            f"Please provide links to open access.\n\n"
            f"Please not that links should be google documents and separated by comma"
        )
        await state.set_state(ButtonHandlerStates.clicked_open_access)

    async def open_access(self, message: Message, state: FSMContext):
        user_id = message.from_user.id
        links = message.text #TODO str >> list
        userdata = self.mongo_client.get_user_data(user_id)
        email = userdata.get("email")
        try:
            self.google_client.share_access_to_document(links, email)
        except GoogleClientException as e:
            await message.answer(str(e))

