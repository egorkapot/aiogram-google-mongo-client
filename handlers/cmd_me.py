from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from google_access_share_bot.utils.utils import setup_logger
import logging


class MeRouter(Router):
    def __init__(self):
        super().__init__()
        self.message.register(self.cmd_me, Command("me"))

    async def cmd_me(self, message: Message, state:FSMContext):
        """Get user information"""
        await state.clear()
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        username = message.from_user.username
        # Construct the message to send back to the user
        response = f"User ID: {user_id}\n"
        response += f"First Name: {first_name}\n"
        response += f"Last Name: {last_name}\n"
        response += f"Username: @{username}"
        await message.answer(response)


