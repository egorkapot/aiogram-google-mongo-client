from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from google_access_share_bot.mongo_client.client import MongoUsersClient
from aiogram import Bot
from google_access_share_bot.settings import Settings
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

        :param bot:
        :param mongo_client: instance of Mongo database
        :param author_chat_id: specific id to log messages
        """
        super().__init__()
        self.bot = bot
        self.mongo_client = mongo_client
        self.author_chat_id = author_chat_id
        self.logger = logging.getLogger(__name__)
        setup_logger(self.logger, self.bot, self.author_chat_id)
        self.message.register(self.start, Command("start"))
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
            self.handle_role, lambda call: call.data.startswith("role_")
        )

    async def start(self, message: Message, state: FSMContext):
        """
        If there is user data in database - proceed with markup

        :param message: message from user
        :param state: current state of user
        :return:
        """
        await state.clear()
        user_id = message.from_user.id
        user_data = self.mongo_client.get_user_data(user_id)
        if user_data:
            role = user_data.get("role")
            markup = create_initial_markup(role)
            await message.answer("Choose what you need", reply_markup=markup)
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

    async def email_is_valid(self, message: Message, state: FSMContext):
        await message.answer(f"The email - {message.text} was sent to approval."
                             f"We will let you know once you have the access")
        await self.bot.send_message(
            self.author_chat_id,
            f"User with parameters:\n"
            f"name: {message.from_user.username}\n"
            f"id: {message.from_user.id}\n"
            f"email: {message.text}\n"
            f"Wants to register. Approve?",
            reply_markup=generate_confirmation_markup(message.from_user.id)
        )
        await state.update_data(username=message.from_user.username.lower())
        await state.update_data(email=message.text.lower())
        user_state = await state.get_data()
        print(user_state)


    async def handle_approve(self, call: CallbackQuery, state: FSMContext):
        user_state = await state.get_data()
        user_state_2 = await state.get_state()
        print(user_state, user_state_2)
        print(1)
        user_id = int(call.data.split("_")[1])
        await self.bot.send_message(
            self.author_chat_id, "Please set the role to user", reply_markup=generate_user_role(user_id)
        )

    async def handle_deny(self, call: CallbackQuery, state: FSMContext):
        print(2)
        user_id = int(call.data.split("_")[1])
        user_state = await state.get_data()
        user_state_2 = await state.get_state()
        print(user_state, user_state_2)
        await self.bot.send_message(user_id, "Registration process was denied by admin @egorkapot")
        await self.bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None  # This removes the inline keyboard
        )
        self.logger.info(f"You have denied the registration for {user_state.get('username')}")
        #await state.clear()

    async def handle_role(self, call: CallbackQuery, state: FSMContext):
        role_ = call.data.split("_")[1]
        await state.update_data(role=f"{role_}")
        await state.set_state(RegistrationStates.awaiting_for_complete_registration)

    async def register_user(self, state: FSMContext):
        data = await state.get_data()
        await self.bot.send_message(self.author_chat_id, f"data is ready to load {data}")





