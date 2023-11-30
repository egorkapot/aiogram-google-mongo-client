from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from google_access_share_bot.bot.bot_package.buttons import (inline_buttons)
from google_access_share_bot.client.mongo_client.client import MongoUsersClient
from google_access_share_bot.client.google_client.client import GoogleClient
from google_access_share_bot.settings import settings


class ButtonHandlerStates(StatesGroup):
    clicked_all_links = State()


class ButtonHandlerRouter(Router):
    def __init__(
            self, bot: Bot, mongo_client: MongoUsersClient, google_client: GoogleClient
    ):
        super().__init__()
        self.bot = bot
        self.google_client = google_client
        self.mongo_client = mongo_client
        self.message.register(
            self.handle_all_links_reply_button,
            F.text == "All Links"
        )
        self.callback_query.register(
            self.handle_all_links_inline_button,
            ButtonHandlerStates.clicked_all_links,
            F.data.startswith("table_")
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

    async def handle_open_the_access(self, message: Message):
        pass
