import json
import logging

from aiogram import Bot
from pymongo import MongoClient, ReturnDocument

from bot.bot import bot
from settings import settings
from utils.utils import setup_logger


class MongoUsersClient:
    """
    Class representation of Mongo Client that is working directly with user collection.
    Logging is done using telegram bot
    """

    def __init__(
        self,
        bot_: Bot,
        chat_id: str | int,
        host: str,
        port: int | None,
        database_name: str,
    ):
        self.client = MongoClient(host, port)
        self.db = self.client[database_name]
        self.initialize_user_collection()
        self.users_collection = self.db.users
        self.bot = bot_
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)
        self.set_validation_schema()
        setup_logger(self.logger, self.bot, self.chat_id, logging.WARNING)

    def initialize_user_collection(self):
        required_collection = "users"
        if required_collection not in self.db.list_collection_names():
            self.db.create_collection(required_collection)

    def set_validation_schema(self):
        """
        Set or update the validation schema for the users' collection.
        """
        with open("client/mongo_client/validation_schema.json", "r") as file:
            validation_schema = json.load(file)

        self.db.command({"collMod": "users", "validator": validation_schema})

    def get_data(self, query: dict, *args) -> list:
        """
        Query MongoDB

        :param query: Query to be sent to MongoDB
        :param args: Query arguments
        :return: List containing MongoDB data
        """
        documents = []
        for document in self.users_collection.find(query, *args):
            documents.append(document)
        return documents

    def get_user_data(self, value: int | str, filter_: str = "_id") -> dict | None:
        """
        Returns all the data about the user.
        By default, searches by _id

        :param filter_: Column to apply filter by default it is _id column
        :param value: Data to search in the database
        :return: User's data
        """
        user_data = self.users_collection.find_one(
            {filter_: value}
        )  # TODO maybe wrap into exception
        return user_data

    def get_username(self, value: int | str, filter_: str = "_id") -> str | None:
        """
        Returns the username of specific user

        :param filter_: Column to apply filter by default it is _id column
        :param value: Data to search in the database
        """
        username = self.users_collection.find_one({filter_: value}).get("username")
        return username

    def add_user(self, user_id: int, data_: dict):
        """
        Adds the user to database

        :param user_id: Unique id of user
        :param data_: Message that contains information to update the user
        :return: None
        """
        try:
            self.users_collection.insert_one(
                {
                    "_id": user_id,
                    "username": data_.get("username"),
                    "role": data_.get("role"),
                    "email": data_.get("email"),
                    "status": data_.get("status"),
                }
            )
            self.logger.info(
                f"Added the user with parameters:\n"
                f"name: {data_.get('username')}\n"
                f"id: {user_id}"
            )
        except Exception as e:
            self.logger.error(
                f"Error registering {user_id} with username: {data_.get('Username')} - {e}"
            )

    def delete_user(self, value: int | str, filter_: str = "_id"):
        """
        Deletes user from users_collection

        :param filter_: Column to apply filter by default it is _id column
        :param value: Data to search in the database
        :return: None
        """
        username = self.get_username(value, filter_)
        self.users_collection.find_one_and_delete(
            {filter_: value}, return_document=ReturnDocument.BEFORE
        )
        self.logger.info(f"Information about {username} was deleted from database")

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
            return_document=ReturnDocument.BEFORE,
        )
        self.logger.warning(f"Information about {username} was changed to {update}")


MONGO_HOST = settings.mongo_host
MONGO_PORT = settings.mongo_port
author_chat_id = settings.author_chat_id
mongo_client = MongoUsersClient(bot, author_chat_id, MONGO_HOST, MONGO_PORT, "db")
