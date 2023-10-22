from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from google_access_share_bot.mongo_client.client import MongoUsersClient
from aiogram import Bot
import logging
from google_access_share_bot.utils.utils import setup_logger
from google_access_share_bot.settings import Settings

class DeleteStates(StatesGroup):
    asked_for_user = State()
class DeleteRouter(Router):
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
        self.message.register(self.cmd_delete, Command("delete"))
        self.admins = Settings().admin_chat_id


    async def cmd_delete(self, message: Message, state: FSMContext):
        #выбрать пользователя - если пользователь есть - запросить ссылку на таблу
        #если ссылка на таблу есть в списке и рабочая - попробовать удалить иначе эрор
        user_id_ = message.from_user.id
        if user_id_ in self.admins:
            await state.set_state(DeleteStates.asked_for_user)
            await message.answer("Please provide telegram's username of user to delete")
        else:
            await message.answer("Prohibited to use admins command")
            self.logger.info(f"{self.mongo_client.get_username(user_id_)} tried to use delete command")

    async def delete_user(self, message: Message, state: FSMContext):
        user_to_delete = message.text
