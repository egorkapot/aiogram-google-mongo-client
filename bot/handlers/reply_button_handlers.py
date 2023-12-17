import logging
import re

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.bot_package.buttons import inline_buttons
from client.google_client.client import GoogleClient, GoogleClientException
from client.mongo_client.client import MongoUsersClient
from settings import settings
from utils.utils import setup_logger


class ButtonHandlerStates(StatesGroup):
    clicked_all_links = State()
    clicked_open_access = State()
    clicked_change_email = State()
    providing_new_email = State()
    clicked_check_for_plagiarism = State()

class ButtonHandlerRouter(Router):
    def __init__(
        self,
        bot: Bot,
        mongo_client: MongoUsersClient,
        google_client: GoogleClient,
        log_chat_id: str,
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
            F.data.startswith("table_"),
        )
        self.message.register(
            self.handle_open_the_access_button, F.text == "Open the access"
        )
        self.message.register(self.open_access, ButtonHandlerStates.clicked_open_access)
        self.message.register(self.change_email, F.text == "Change my email")
        self.callback_query.register(
            self.handle_deny_change_email,
            ButtonHandlerStates.clicked_change_email,
            F.data.startswith("deny_"),
        )
        self.callback_query.register(
            self.handle_approve_change_email,
            ButtonHandlerStates.clicked_change_email,
            F.data.startswith("approve_"),
        )
        self.message.register(
            self.update_with_new_email, ButtonHandlerStates.providing_new_email
        )
        self.message.register(
            self.check_for_plagiarism,
            F.text == "Check for plagiarism"
        )

    async def handle_all_links_reply_button(
        self, message: Message, state: FSMContext
    ) -> None:
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
            reply_markup=inline_buttons.generate_all_link_markup(user_role),
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

    async def handle_open_the_access_button(
        self, message: Message, state: FSMContext
    ) -> None:
        """
        Triggers when user clicked open access function.
        Asks user to provide links to open access.

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        await message.answer(
            f"Please provide links to open access.\n\n"
            f"Please note that links should be google documents"
        )
        await state.set_state(ButtonHandlerStates.clicked_open_access)

    async def open_access(self, message: Message, state: FSMContext) -> None:
        """
        Splits the incoming links and divide them by valid and non-valid links
        Open the access to valid links using google client.
        Send notification message to user mentioning non-valid links

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        user_id = message.from_user.id
        links = message.text
        list_of_links = re.split(r"[ ,\n]+", links)
        userdata = self.mongo_client.get_user_data(user_id)
        email = userdata.get("email")
        valid_links = [
            link
            for link in list_of_links
            if self.google_client.is_google_document(link)
        ]
        invalid_links = set(list_of_links) - set(valid_links)
        self.google_client.share_access_to_document(valid_links, email)
        valid_links_text = "\n\n".join(valid_links)
        if not invalid_links:
            await message.answer(
                f"Access should be opened for the following links: {valid_links_text}"
            )
        else:
            invalid_links_message = "\n\n".join(invalid_links)
            await message.answer(
                f"Access should be opened for the following links: {valid_links_text}\n\n"
                f"Links that are not google documents: {invalid_links_message}"
            )
        await state.clear()

    async def change_email(self, message: Message, state: FSMContext) -> None:
        """
        Triggers when user click Change my email button.
        Generate markup to user to accept or decline change of email
        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        user_id = message.from_user.id
        userdata = self.mongo_client.get_user_data(user_id)
        email = userdata.get("email")
        await message.answer(
            f"Your current email is: {email}\n\n"
            f"Are you sure you want to change it?",
            reply_markup=inline_buttons.generate_confirmation_markup(user_id),
        )
        await state.set_state(ButtonHandlerStates.clicked_change_email)

    async def handle_deny_change_email(
        self, call: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Denies changing email. Clears state of user

        :param call: Call from markup
        :param state: Current state of user
        :return: None
        """
        await call.message.edit_text(f"You have denied process of changing email")
        await state.clear()

    async def handle_approve_change_email(
        self, call: CallbackQuery, state: FSMContext
    ) -> None:
        """
        Approves changing email. Asks user to provide new email

        :param call: Call from markup
        :param state: Current state of user
        :return: None
        """
        await call.message.edit_text(f"Please provide your new email")
        await state.set_state(ButtonHandlerStates.providing_new_email)

    async def update_with_new_email(self, message: Message, state: FSMContext) -> None:
        """
        Validates that new email matches the requirements.
        If yes - updates the database with new email

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        user_id = message.from_user.id
        new_email = message.text
        if self.google_client.is_google_email(new_email):
            self.mongo_client.update_user(user_id, {"email": new_email})
            await message.answer(f"Your email was changed to {new_email}")
            await state.clear()
        else:
            await message.answer(
                f"Email: {new_email} does not match the requirements.\n\n"
                f"Try again or choose /cancel command"
            )

    async def check_for_plagiarism(self, message: Message, state: FSMContext):
        await message.answer("Not implemented yet") #TODO

