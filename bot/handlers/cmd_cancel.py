import logging

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from utils.utils import setup_logger


class CancelRouter(Router):
    def __init__(self):
        super().__init__()
        self.message.register(self.cmd_cancel, Command("cancel"))

    @staticmethod
    async def cmd_cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            text="Action was cancelled. You can start again using /start command or others",
            reply_markup=ReplyKeyboardRemove(),
        )
