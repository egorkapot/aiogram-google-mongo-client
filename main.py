import os
import json

import telebot
from dotenv import load_dotenv
from telebot import types

from google_access_share_bot.credentials.client import Client
from google_access_share_bot.emails.emails import get_emails_list
from google_access_share_bot.utils.utils import (
    is_google_document,
    is_google_spreadsheet,
)
from googleapiclient.errors import HttpError


load_dotenv()
bot_token = os.environ.get("DEVELOPMENT_BOT_TOKEN")
admin_chat_id = os.environ.get("ADMIN_CHAT_ID").split(",")
bot = telebot.TeleBot(bot_token)
list_of_emails = get_emails_list()
user_data = {}
client = Client(bot, admin_chat_id)

users_asked_for_link = set()


def send_message_to_user(user_id, message, **kwargs):
    """Sends message to specific user"""
    bot.send_message(user_id, message, **kwargs)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    open_access = types.KeyboardButton("Open the access")
    link_to_table = types.KeyboardButton("Working Table")
    link_to_guide = types.KeyboardButton("Link to Guide")
    markup.row(link_to_table, link_to_guide)
    markup.row(open_access)
    bot.send_message(message.from_user.id, "Choose what you need", reply_markup=markup)


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
        client.logger.error(f"{user_id} tried to access cleantable")


@bot.callback_query_handler(func=lambda call: call.data == "provide_link")
def ask_for_link(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "Please provide a link")
    users_asked_for_link.add(call.from_user.id)


@bot.message_handler(func=lambda message: message.from_user.id in users_asked_for_link)
def clean_the_spreadsheet(message):
    user_id = message.from_user.id
    link = message.text
    if is_google_spreadsheet(link):
        try:
            client.clean_spreadsheet(link)
            send_message_to_user(user_id, "Spreadsheet was cleaned")
            client.logger.info(f"Cleaned the spreadsheet - {link}")
        except HttpError as error:
            send_message_to_user(user_id, f"An error occurred {error}")
            client.logger.error(
                f"Failed to clean the spreadsheet - {link} due to {error}"
            )
    else:
        send_message_to_user(user_id, "Provided link is not a google spreadsheet")
    users_asked_for_link.remove(message.from_user.id)


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


# @bot.message_handler(func=lambda message: message.text == 'Open the access')
# def open_access(message):
#     user_id = message.from_user.id
#     if user_id:
#         pass
#     else:
#         send_message_to_user(user_id, "Sorry I cant handle your request")


if __name__ == "__main__":
    bot.infinity_polling()
