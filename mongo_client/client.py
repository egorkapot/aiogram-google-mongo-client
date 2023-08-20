import logging

from pymongo import MongoClient
from pymongo import ReturnDocument
import telebot
import json
from google_access_share_bot.bot_logging.admin_logging import BotAdminLoggingHandler


class MongoUsersClient:
    """
    Class representation of Mongo Client that is working directly with user collection.
    Logging is done using telegram bot
    """
    def __init__(self, bot_: telebot.TeleBot, chat_id: str | int, host: str, port: int | None, database_name: str):
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.users_collection = self.db.users
        self.bot = bot_
        self.chat_id = chat_id
        self.logger = logging.getLogger("mongo_logger")
        self.setup_logger()
        self.set_validation_schema()

    def setup_logger(self):
        handler = BotAdminLoggingHandler(self.bot, self.chat_id)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%y-%m-%d"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def set_validation_schema(self):
        """
        Set or update the validation schema for the users collection.
        """
        with open("validation_schema.json", "r") as file:
            validation_schema = json.load(file)

        self.db.command({
            "collMod": "users",
            "validator": validation_schema
        })

    def get_user_data(self, user_id: int) -> dict | None:
        """
        Returns all the data about the user

        :param user_id: Unique id of user
        :return: Data about the user or None
        """
        user_data = self.users_collection.find_one(
            {"_id": user_id}
        )
        return user_data

    def get_username(self, user_id: int) -> str | None:
        """
        Returns the username of specific user

        :param user_id: Unique id of user
        :return: Username of user or None
        """
        username = self.get_user_data(user_id).get("username")
        return username

    def add_user(self, user_id: int, data_):
        """
        Adds the user to database

        :param user_id: Unique id of user
        :param data_: Message that contains information to update the user
        :return: None
        """
        try:
            self.users_collection.insert_one(
                {"_id": user_id,
                 "username": data_.get('Username'),
                 "role": "user",
                 "email": None,
                 "status": "registered",
                 "state": None})
            self.logger.info(f"Registered {data_.get('Username')} with id - {user_id}")
        except Exception as e:
            self.logger.error(f"Error registering {user_id} with username: {data_.get('Username')} - {e}")

    def delete_user(self, user_id: int):
        """
        Deletes user from users_collection

        :param user_id: Unique id of user
        """
        username = self.get_username(user_id)
        self.users_collection.find_one_and_delete(
            {"_id": user_id},
            return_document=ReturnDocument.BEFORE
        )
        self.logger.info(
            f'Information about {username} was deleted from database'
        )

    def update_user(self, user_id: int, update: dict, upsert=False) -> None:
        """
        Updates users information if _id is found.

        :param user_id: Unique id of user
        :param update: Information to update that should be specified in {}
        :param upsert: If upsert is True and no documents match the filter, a new document will be created.
        If upsert is False and no documents match the filter, no action will be taken.
        :type upsert: True or False
        """
        username = self.get_username(user_id)
        self.users_collection.find_one_and_update(
            {"_id": user_id},
            {"$set": update},
            upsert=upsert,
            return_document=ReturnDocument.BEFORE
        )
        self.logger.info(
            f'Information about {username} was changed to {update}'
        )
