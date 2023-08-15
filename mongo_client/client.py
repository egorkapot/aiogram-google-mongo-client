import logging
import os

from dotenv import load_dotenv
from pymongo import MongoClient

from google_access_share_bot.bot_logging.admin_logging import BotAdminLoggingHandler

load_dotenv()
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))


class MongoClientTgBot:
    def __init__(self, bot, chat_id, host, port, database_name):
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.users_collection = self.db.users
        self.bot = bot
        self.chat_id = chat_id
        self.logger = logging.getLogger("mongo_logger")

    def setup_logger(self):
        handler = BotAdminLoggingHandler(self.bot, self.chat_id)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%y-%m-%d"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
