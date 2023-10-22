from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot
from google_access_share_bot.utils.utils import setup_logger
import logging


class CancelRouter(Router):
    def __init__(self):
        super().__init__()
        self.message.register(self.cmd_cancel, Command("cancel"))

    async def cmd_cancel(self, message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            text="Action was cancelled. You can start again using /start command or others",
            reply_markup=ReplyKeyboardRemove()
        )


