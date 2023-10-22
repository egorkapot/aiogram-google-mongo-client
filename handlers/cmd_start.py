from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from google_access_share_bot.mongo_client.client import MongoUsersClient
from aiogram import Bot
from google_access_share_bot.bot_package.buttons import (
    create_initial_markup, generate_confirmation_markup, generate_user_role)
import logging
from google_access_share_bot.utils.utils import setup_logger, is_google_email


class RegistrationStates(StatesGroup):
    awaiting_for_email = State()
    awaiting_for_complete_registration = State()


class RegistrationRouter(Router):
    def __init__(self, bot: Bot, mongo_client: MongoUsersClient, author_chat_id: str):
        """
        Initialisation of the Mongo client, bot instance to handle bot-specific
        functions that are not supported by methods of Message class.

        :param bot: instance of telebot
        :param mongo_client: instance of Mongo database
        :param author_chat_id: specific id to log messages
        """
        super().__init__()
        self.bot = bot
        self.mongo_client = mongo_client
        self.author_chat_id = author_chat_id
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger, self.bot, self.author_chat_id)
        self.message.register(self.cmd_start, Command("start"))
        self.message.register(
            self.email_is_valid,
            RegistrationStates.awaiting_for_email,
            F.text.func(lambda text: is_google_email(text)))
        self.message.register(self.email_is_not_valid, RegistrationStates.awaiting_for_email)
        self.callback_query.register(
            self.handle_approve, F.data.startswith("approve_")
        )
        self.callback_query.register(
            self.handle_deny,
            F.data.startswith("deny_")
        )
        self.callback_query.register(
            self.handle_role, F.data.startswith("role_")
        )

    async def cmd_start(self, message: Message, state: FSMContext):
        """
        If there is user data in database, and he is registered - proceed with markup
        If there is user data but status is not registered or there is no data at all-send to registration

        :param message: message from user
        :param state: current state of user
        :return:
        """
        await state.clear()
        user_id_ = message.from_user.id
        user_data = self.mongo_client.get_user_data(user_id_)
        if user_data and user_data.get("status") == "registered":
            role = user_data.get("role")
            markup = create_initial_markup(role)
            await message.answer("Choose what you need", reply_markup=markup)
        elif user_data and user_data.get("status") != "registered":
            self.mongo_client.delete_user(user_id_)
            await message.answer("Registration process created, please provide your email")
            await state.set_state(RegistrationStates.awaiting_for_email)
        else:
            await message.answer("Registration process created, please provide your email")
            await state.set_state(RegistrationStates.awaiting_for_email)

    async def email_is_not_valid(self, message: Message) -> None:
        """
        Respond the user that email is not valid
        :param message: incoming message from user
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
        :param message: message from user
        :param state: current state of user
        :return: None
        """
        user_id_ = int(message.from_user.id)
        await message.answer(f"The email - {message.text} was sent to approval.\n\n"
                             f"We will let you know once you have the access")
        await state.update_data(username=message.from_user.username.lower())
        await state.update_data(email=message.text.lower())
        user_state = await state.get_data()
        self.mongo_client.add_user(user_id_, user_state)
        await self.bot.send_message(
            self.author_chat_id,
            f"User with parameters:\n\n"
            f"name: {message.from_user.username}\n"
            f"id: {user_id_}\n"
            f"email: {message.text}\n"
            f"Wants to register. Approve?",
            reply_markup=generate_confirmation_markup(message.from_user.id)
        )
        await state.clear()

    async def handle_approve(self, call: CallbackQuery) -> None:
        """
        Proceed if admin approves the user's registration.
        Extracts the user_id from call data and creates a markup for admin with role buttons.
        :param call: call from markup
        :return: None
        """
        user_id_ = int(call.data.split("_")[1])
        await self.bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None  # This removes the inline keyboard
        )
        await self.bot.send_message(
            self.author_chat_id, "Please set the role to user", reply_markup=generate_user_role(user_id_)
        )
        self.mongo_client.update_user(user_id_, {"status": "awaiting_for_role"})

    async def handle_deny(self, call: CallbackQuery) -> None:
        """
        Proceed if admin denies the user's registration.
        Deletes the user from database and sends the message to user and author

        :param call: call from markup
        :return: None
        """
        user_id_ = int(call.data.split("_")[1])
        await self.bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None  # This removes the inline keyboard
        )
        await self.bot.send_message(
            user_id_, "Registration process was denied by admin @egorkapot"
        )
        username = self.mongo_client.get_username(user_id_)
        self.logger.info(f"You have denied the registration for {username}")
        self.mongo_client.delete_user(user_id_)

    async def handle_role(self, call: CallbackQuery) -> None:
        """
        Creates role for user and finishes registration in database
        :param call:
        :return:
        """
        await self.bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None  # This removes the inline keyboard
        )
        user_id_ = int(call.data.split("_")[2])
        role_ = call.data.split("_")[1]
        self.mongo_client.update_user(user_id_, {"role": role_, "status": "registered"})
        self.logger.info(f"{self.mongo_client.get_username(user_id_)} was registered with the role - {role_}")
        await self.bot.send_message(
            user_id_, "You have been registered! Please see the available options",
            reply_markup=create_initial_markup(role_)
        )




