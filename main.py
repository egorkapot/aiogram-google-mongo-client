import logging
import os

import telebot
from dotenv import load_dotenv
from googleapiclient.errors import HttpError
from telebot import types

from google_access_share_bot.bot_logging.user_logging import BotUserLoggingHandler
from google_access_share_bot.bot_package import buttons
from google_access_share_bot.google_client.client import GoogleClient
from google_access_share_bot.mongo_client.client import MongoUsersClient
from google_access_share_bot.utils.utils import (
    is_google_document,
    is_google_spreadsheet,
)

load_dotenv()
bot_token = os.environ.get("DEVELOPMENT_BOT_TOKEN")
author_chat_id = os.environ.get("AUTHOR_CHAT_ID")  # Chat id of creator for logging
admin_chat_id = os.environ.get("ADMIN_CHAT_ID").split(",")
bot = telebot.TeleBot(bot_token)
google_client = GoogleClient(bot, admin_chat_id)
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
mongo_client = MongoUsersClient(bot, author_chat_id, MONGO_HOST, MONGO_PORT, 'db')


def setup_user_logging(bot_instance: telebot.TeleBot):
    """Set up logger for users using BotUserLoggingHandler that determines the logic of processing messages"""
    logger = logging.getLogger("user_logging")
    handler = BotUserLoggingHandler(bot_instance)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%y-%m-%d"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger, handler


user_logger, user_handler = setup_user_logging(bot)


def send_message_to_user(user_id, message, **kwargs):
    """Sends message to specific user"""
    bot.send_message(user_id, message, **kwargs)


@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_data = mongo_client.get_user_data(user_id)
    if user_data:
        role = user_data.get('role') #TODO продолжить логику с регистрацией и кнопками по ролям
    else:
        bot.send_message(message.from_user.id, "Choose what you need", reply_markup=buttons.user_markup)


@bot.message_handler(commands=["cleantable"])
def validate_user_to_clean_table(message):
    user_id = message.from_user.id
    if str(user_id) in admin_chat_id:
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("Provide Link", callback_data="provide_link")
        )
        send_message_to_user(
            user_id, "Authenticated, now provide link to table", reply_markup=markup
        )
    else:
        send_message_to_user(user_id, "You are not the admin")
        google_client.logger.info(f"{user_id} tried to access cleantable")

#
# @bot.callback_query_handler(func=lambda call: call.data == "provide_link")
# def ask_for_link(call):
#     bot.answer_callback_query(call.id)
#     bot.send_message(call.from_user.id, "Please provide a link")
#     users_asked_for_link.add(call.from_user.id)
#
#
# @bot.message_handler(func=lambda message: message.from_user.id in users_asked_for_link)
# def clean_the_spreadsheet(message):
#     user_id = message.from_user.id
#     link = message.text
#     if is_google_spreadsheet(link):
#         try:
#             google_client.clean_spreadsheet(link)
#             send_message_to_user(user_id, "Spreadsheet was cleaned")
#             google_client.logger.info(f"Cleaned the spreadsheet - {link}")
#         except HttpError as error:
#             send_message_to_user(user_id, f"An error occurred {error}")
#             google_client.logger.error(
#                 f"Failed to clean the spreadsheet - {link} due to {error}"
#             )
#     else:
#         send_message_to_user(user_id, "Provided link is not a google spreadsheet")
#     users_asked_for_link.remove(message.from_user.id)


@bot.message_handler(commands=["me"])
def me_command(message):
    """Get user information"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    # Construct the message to send back to the user
    response = f"User ID: {user_id}\n"
    response += f"First Name: {first_name}\n"
    response += f"Last Name: {last_name}\n"
    response += f"Username: @{username}"
    user_handler.set_chat_id(author_chat_id)
    user_logger.info(f'{message.from_user.username} requested information about himself')
    send_message_to_user(user_id, response)


@bot.message_handler(func=lambda message: message.text == "Working Table")
def send_link_to_working_table(message):
    """Send the user a link"""
    user_id = message.from_user.id
    send_message_to_user(user_id, os.environ.get("TABLE_LINK"))


@bot.message_handler(func=lambda message: message.text == "Link to Guide")
def send_link_to_guide(message):
    user_id = message.from_user.id
    send_message_to_user(user_id, os.environ.get("GUIDE_LINK"))


if __name__ == "__main__":
    bot.infinity_polling()
