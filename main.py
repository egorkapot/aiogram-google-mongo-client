import os

import telebot
from dotenv import load_dotenv
from telebot import types

from credentials.client import Client
from emails.emails import get_emails_list
from utils.utils import is_valid_link

load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")
author_chat_id = os.environ.get("AUTHOR_CHAT_ID")
bot = telebot.TeleBot(bot_token)
list_of_emails = get_emails_list()
user_data = {}
client = Client(bot, author_chat_id)


def send_message_to_user(user_id, message):
    bot.send_message(user_id, message)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    open_access = types.KeyboardButton("Open the access")
    link_to_table = types.KeyboardButton("Working Table")
    link_to_guide = types.KeyboardButton("Link to Guide")
    markup.row(link_to_table, link_to_guide)
    markup.row(open_access)
    bot.send_message(message.from_user.id, "Choose what you need", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def message_handling(message):
    user_id = message.from_user.id
    if message.text == "Open the access":
        initiate_access_request(user_id)
    elif message.text == "Working Table":
        send_message_to_user(user_id, os.environ.get("TABLE_LINK"))
    elif message.text == "Link to Guide":
        send_message_to_user(user_id, os.environ.get("GUIDE_LINK"))
    elif user_id in user_data:
        handle_access_request(user_id, message.text)
    else:
        send_message_to_user(user_id, "Sorry I cant handle your request")


def handle_access_request(user_id, message):
    if user_data[user_id]["state"] == "awaiting_email":
        handle_email(user_id, message)
    elif user_data[user_id]["state"] == "awaiting_link":
        handle_link(user_id, message)
    else:
        client.logger.error("Unable to define state of the user")


def initiate_access_request(user_id):
    user_data[user_id] = {
        "state": "awaiting_email",
        "email": None,
        "link": None,
    }
    send_message_to_user(user_id, "Provide your email")


def handle_email(user_id, email):
    if email in list_of_emails:
        user_data[user_id]["email"] = email
        user_data[user_id]["state"] = "awaiting_link"
        send_message_to_user(user_id, "Now provide the link to the document")
    else:
        send_message_to_user(user_id, "Incorrect email, please try again")


def handle_link(user_id, link):
    file_id = is_valid_link(link)
    if file_id:
        send_message_to_user(user_id, "Access will be opened shortly")
        email = user_data[user_id].get("email")
        client.share_document(file_id, email)
        del user_data[user_id]
    else:
        send_message_to_user(user_id, "Invalid link, please try again")


if __name__ == "__main__":
    bot.infinity_polling()
