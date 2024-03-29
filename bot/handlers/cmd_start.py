import logging
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.bot_package.buttons import inline_buttons, reply_buttons
from client.google_client.client import google_client
from client.mongo_client.client import MongoUsersClient
from settings import settings
from utils.utils import setup_logger
from aiogram.exceptions import TelegramBadRequest


class RegistrationStates(StatesGroup):
    awaiting_for_email = State()
    awaiting_for_complete_registration = State()


class RegistrationRouter(Router):
    def __init__(self, bot: Bot, mongo_client: MongoUsersClient, log_chat_id: str):
        """
        Initialisation of the Mongo client, bot instance to handle bot-specific
        functions that are not supported by methods of Message class.

        :param bot: Instance of telebot
        :param mongo_client: Instance of Mongo database
        :param log_chat_id: Specific id to log messages
        """
        super().__init__()
        self.bot = bot
        self.mongo_client = mongo_client
        self.log_chat_id = log_chat_id
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger, self.bot, self.log_chat_id, logging.WARNING)
        self.message.register(self.cmd_start, Command("start"))
        self.message.register(
            self.email_is_valid,
            RegistrationStates.awaiting_for_email,
            F.text.func(lambda text: google_client.is_google_email(text)),
        )
        self.message.register(
            self.email_is_not_valid, RegistrationStates.awaiting_for_email
        )
        self.callback_query.register(self.handle_approve, F.data.startswith("registration_approve_"))
        self.callback_query.register(self.handle_deny, F.data.startswith("registration_deny_"))
        self.callback_query.register(self.handle_role, F.data.startswith("role_"))

    async def cmd_start(self, message: Message, state: FSMContext):
        """
        If there is user data in database, and he is registered - proceed with markup
        If there is user data but status is not registered or there is no data at all-send to registration

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        await state.clear()
        user_id_ = message.from_user.id
        user_data = self.mongo_client.get_user_data(user_id_)
        if user_data and user_data.get("status") == "registered":
            role = user_data.get("role")
            markup = reply_buttons.create_initial_markup(role)
            await message.answer("Choose what you need", reply_markup=markup)
        elif user_data and user_data.get("status") != "registered":
            self.mongo_client.delete_user(user_id_)
            await message.answer(
                "Registration process created, please provide your email"
            )
            await state.set_state(RegistrationStates.awaiting_for_email)
        else:
            await message.answer(
                "Registration process created, please provide your email"
            )
            await state.set_state(RegistrationStates.awaiting_for_email)

    @staticmethod
    async def email_is_not_valid(message: Message) -> None:
        """
        Respond the user that email is not valid

        :param message: Message from user
        :return: None
        """
        await message.answer(
            f"Provided email: {message.text} is not valid please try again or contact the admin: @egorkapot"
        )

    async def email_is_valid(self, message: Message, state: FSMContext) -> None:
        """
        Proceed if user's email is valid. Updates the user's state and adds it to database.
        Sends the author a message for approval with the user's parameters and confirmation markup.
        Clears the user's state in the end.

        :param message: Message from user
        :param state: Current state of user
        :return: None
        """
        try:
            await state.update_data(
                username=message.from_user.username.lower())
        except AttributeError:
            await message.answer(f"Your username was not found.\n\n"
                                 f"Please check your username in the settings and try again.")
            return
        user_id_ = int(message.from_user.id)
        await message.answer(
            f"The email - {message.text} was sent to approval.\n\n"
            f"We will let you know once you have the access"
        )
        await state.update_data(email=message.text.lower())
        user_state = await state.get_data()
        self.mongo_client.add_user(user_id_, user_state)
        await self.bot.send_message(
            self.log_chat_id,
            f"User with parameters:\n\n"
            f"name: {message.from_user.username}\n"
            f"id: {user_id_}\n"
            f"email: {message.text}\n"
            f"Wants to register. Approve?",
            reply_markup=inline_buttons.generate_confirmation_markup(
                "registration", message.from_user.id
            ),
        )
        await state.clear()

    async def handle_approve(self, call: CallbackQuery) -> None:
        """
        Proceed if admin approves the user's registration.
        Extracts the user_id from call data and creates a markup for admin with role buttons.
        :param call: Call from markup
        :return: None
        """
        user_id_ = int(call.data.split("_")[2])
        await call.message.edit_text(
            "Please set the role to user",
            reply_markup=inline_buttons.generate_user_role(user_id_),
        )
        self.mongo_client.update_user(user_id_, {"status": "awaiting_for_role"})

    async def handle_deny(self, call: CallbackQuery) -> None:
        """
        Proceed if admin denies the user's registration.
        Deletes the user from database and sends the message to user and author

        :param call: Call from markup
        :return: None
        """
        user_id_ = int(call.data.split("_")[2])
        username = self.mongo_client.get_username(user_id_)
        await call.message.edit_text(
            f"You have denied the registration for user: {username}",
            reply_markup=None
        )
        await self.bot.send_message(
            user_id_, "Registration process was denied by admin @egorkapot"
        )
        self.logger.info(f"Registration for {username} was denied")
        self.mongo_client.delete_user(user_id_)

    async def handle_role(self, call: CallbackQuery) -> None:
        """
        Creates role for user and finishes registration in database

        :param call: Call from markup
        :return:
        """
        user_id_ = int(call.data.split("_")[2])
        role_ = call.data.split("_")[1]
        self.mongo_client.update_user(user_id_, {"role": role_, "status": "registered"})
        await call.message.edit_text(
            f"{self.mongo_client.get_username(user_id_)} was registered with the role - {role_}",
            reply_markup=None
        )
        await self.bot.send_message(
            user_id_,
            "You have been registered! Please see the available options",
            reply_markup=reply_buttons.create_initial_markup(role_),
        )
        if role_ != "biggiko":
            try:
                chat_invite_link = await self.bot.export_chat_invite_link(
                    chat_id=settings.web_content_chat_id
                )
                await self.bot.send_message(
                    user_id_, text=f"Your invite link: {chat_invite_link}"
                )
            except TelegramBadRequest as error:
                self.logger.error(f"Error while sending invite link {error}")
