import logging
from datetime import timedelta

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.bot_package.buttons import inline_buttons
from client.google_client.client import GoogleClient, GoogleClientException
from client.mongo_client.client import MongoUsersClient
from settings import settings
from utils.utils import setup_logger


class DeleteStates(StatesGroup):
    asked_for_user_name = State()
    choosing_table_links = State()
    confirming_selection = State()


class DeleteRouter(Router):
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
        self.message.register(self.handle_delete_button, F.text == "Delete User")
        self.message.register(self.validate_user_name, DeleteStates.asked_for_user_name)
        self.callback_query.register(
            self.handle_table_button_click,
            F.data.startswith("table_"),
            DeleteStates.choosing_table_links,
        )
        self.callback_query.register(
            self.skip_table_selection,
            F.data == "skip",
            DeleteStates.choosing_table_links,
        )
        self.callback_query.register(
            self.confirm_table_selection,
            F.data == "confirm",
            DeleteStates.choosing_table_links,
        )
        self.callback_query.register(
            self.deny_selection, F.data == "deny", DeleteStates.confirming_selection
        )
        self.callback_query.register(
            self.delete_user, F.data == "confirm", DeleteStates.confirming_selection
        )

    async def handle_delete_button(self, message: Message, state: FSMContext):
        """
        Validates that the user is admin. Asks to provide a username to delete

        :param message: Message from user
        :param state: Current state of user
        :return:
        """
        await state.clear()
        user_id_ = message.from_user.id
        try:
            user_role_ = self.mongo_client.get_user_data(user_id_).get("role")
        except AttributeError as e:
            await message.answer(f"You are not registered user!")
            return
        if user_role_ == "admin":
            userdata = self.mongo_client.get_data(
                {}, {"username": 1, "email": 1, "_id": 0}
            )
            userdata_text = "\n\n".join(
                f"{index}. "
                f"Username: {userdata_['username']}, "
                f"Email: {userdata_['email']}"
                for index, userdata_ in enumerate(userdata, start=1)
            )
            await state.set_state(DeleteStates.asked_for_user_name)
            await message.answer(
                f"<b>Current users are</b>: \n\n{userdata_text}\n\n"
                f"\n<b>Please provide telegram's username of user to delete</b>",
                parse_mode="HTML",
            )
        else:
            await message.answer("Prohibited to use admins command")
            self.logger.info(
                f"{message.from_user.username} tried to use delete command"
            )

    async def validate_user_name(self, message: Message, state: FSMContext):
        """
        Checks that a user exists in the database before deleting, creates a markup of table's names

        :param message: Message from user
        :param state: Current state of user
        :return:
        """
        user_to_delete_ = message.text.lower()
        userdata = self.mongo_client.get_user_data(user_to_delete_, filter_="username")
        if userdata:
            await state.update_data(user_id=userdata.get("_id", ""))
            await state.update_data(user_to_delete=user_to_delete_)
            await state.update_data(email=userdata.get("email", ""))
            await state.set_state(DeleteStates.choosing_table_links)
            await message.answer(
                "Please choose a table where to remove user's access.\n\n"
                "Keep in mind that you will need to delete his list manually",
                reply_markup=inline_buttons.generate_markup(
                    [
                        inline_buttons.working_tables_markup,
                        [inline_buttons.confirm_button, inline_buttons.skip_button],
                    ]
                ),
            )
        else:
            await message.answer(
                f"No user with username: {user_to_delete_} was found in the database"
            )

    @staticmethod
    async def handle_table_button_click(call: CallbackQuery, state: FSMContext) -> None:
        """
        Retrieves the table name from callback. Checks if there is a list of selected tables in states.
        Appends current table to this list, excludes the selection from the markup.

        :param call: Call from markup
        :param state: Current state of user
        :return:
        """
        table = call.data.split("table_")[1]
        userdata = await state.get_data()
        selected_tables = userdata.get("selected_tables", [])
        if table not in selected_tables:
            selected_tables.append(table)
        await state.update_data(selected_tables=selected_tables)
        new_markup = inline_buttons.create_markup_excluding(
            call.data, call.message.reply_markup
        )
        selected_tables_text = ", ".join(selected_tables)
        await call.message.edit_text(
            f"You selected <b>{selected_tables_text}</b>.\n\n"
            f"Click confirm to proceed with selection.\n\n"
            f"You can skip the selection by clicking <b>Skip</b> button",
            reply_markup=new_markup,
            parse_mode="HTML",
        )

    @staticmethod
    async def skip_table_selection(call: CallbackQuery, state: FSMContext):
        """
        If users clicks on skip during selection - removes tables from selection.
        Provides confirmation markup

        :param call: Call from markup
        :param state: Current state of user
        :return:
        """
        await state.update_data(selected_tables=None)
        userdata = await state.get_data()
        await call.message.edit_text(
            f"You have skipped the selection of tables.\n\n"
            f"Please confirm the deletion of the following user:\n\n"
            f"Username: {userdata.get('user_to_delete')}\n\n",
            reply_markup=inline_buttons.generate_markup(
                [[inline_buttons.confirm_button, inline_buttons.deny_button]]
            ),
        )
        await state.set_state(DeleteStates.confirming_selection)

    @staticmethod
    async def confirm_table_selection(call: CallbackQuery, state: FSMContext) -> None:
        """
        Triggered after user confirms the selection of tables.
        Send the information about the user to delete and list of selected tables.
        Asks again for final confirmation.

        :param call: Call from markup
        :param state: Current state of user
        :return: None
        """
        userdata = await state.get_data()
        selected_tables = userdata.get("selected_tables", [])
        table_links = {
            table: settings.get_table_link(table) for table in selected_tables
        }
        if table_links:
            tables_text = "\n\n".join(
                f"{table} - {link}" for table, link in table_links.items()
            )
            await state.update_data(table_links=table_links)
        else:
            tables_text = "No tables were selected"
        await call.message.edit_text(
            f"Please confirm the deletion of the following user:\n\n"
            f"Username: @{userdata.get('user_to_delete')}\n\n"
            f"Email: {userdata.get('email')}\n\n"
            f"Tables to remove from:\n\n {tables_text}",
            reply_markup=inline_buttons.generate_markup(
                [[inline_buttons.confirm_button]]
            ),
        )
        await state.set_state(DeleteStates.confirming_selection)

    async def deny_selection(self, call: CallbackQuery, state: FSMContext) -> None:
        """
        Denies the deletion of user

        :param call: Call from markup
        :param state: Current state of user
        :return: None
        """
        await call.message.edit_text("You have denied the deletion of user")
        await state.clear()

    async def delete_user(self, call: CallbackQuery, state: FSMContext) -> None:
        """
        Deletes user from database and removes the access from each google document.
        Finds permission ID by provided email in each document and deletes this permission in the document.
        Sends the information message to admin that user was deleted

        :param call: Call from markup
        :param state: Current state of user
        :return: None
        """
        userdata = await state.get_data()
        table_links = userdata.get("table_links")
        user_id = userdata.get("user_id")
        email = userdata.get("email")
        user_to_delete = userdata.get("user_to_delete")
        selected_tables = []
        if table_links:
            for table, link in table_links.items():
                try:
                    permission_id = self.google_client.get_permission_id(link, email)
                except GoogleClientException as e:
                    self.logger.error(e)
                    return
                if permission_id:
                    selected_tables.append(table)
                    self.google_client.remove_access(link, permission_id)
                else:
                    await call.message.answer(
                        f"Email: {email} is not present in {table} - {link}"
                    )
        self.mongo_client.delete_user(value=user_to_delete, filter_="username")
        selected_tables_text = ", ".join(selected_tables)
        if selected_tables_text:
            await call.message.edit_text(
                f"User: @{user_to_delete} was deleted from the database"
                f" and the following tables: \n\n {selected_tables_text}"
            )
        else:
            await call.message.edit_text(
                f"User: @{user_to_delete} was deleted from database but was not matched with tables to delete from"
            )
        await self.bot.ban_chat_member(
            chat_id=settings.web_content_chat_id,
            user_id=user_id,
            until_date=timedelta(minutes=1),
            revoke_messages=True,
        )
        await self.bot.send_message(
            chat_id=settings.web_content_chat_id,
            text=f"User: {user_to_delete} was banned",
        )
