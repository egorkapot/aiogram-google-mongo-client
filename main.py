import os

import telebot
from dotenv import load_dotenv
from telebot import types

from google_access_share_bot.credentials.client import Client
from google_access_share_bot.emails.emails import get_emails_list
from google_access_share_bot.utils.utils import is_google_document, is_google_spreadsheet, validate_admin

load_dotenv()
bot_token = os.environ.get("DEVELOPMENT_BOT_TOKEN")
admin_chat_id = os.environ.get("ADMIN_CHAT_ID").split(',')
bot = telebot.TeleBot(bot_token)
list_of_emails = get_emails_list()
user_data = {}
client = Client(bot, admin_chat_id)


def send_message_to_user(user_id, message):
    """Sends message to specific user"""
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

@bot.message_handler(commands=["clean table"]) #TODO not sure if can skip underscore in naming
def clean_working_table(message, table_id):
    user_id = message.from_user.id
    if validate_admin(user_id, admin_chat_id):
        #TODO todo
    else:
        client.logger.error("You are not the admin :)")


@bot.message_handler(func=lambda message: message.text == 'Working Table')
def send_link_to_working_table(message):
    user_id = message.from_user.id
    send_message_to_user(user_id, os.environ.get("TABLE_LINK"))

@bot.message_handler(func=lambda message: message.text == 'Link to Guide')
def send_link_to_guide(message):
    user_id = message.from_user.id
    send_message_to_user(user_id, os.environ.get("GUIDE_LINK"))

@bot.message_handler(func=lambda message: message.text == 'Open the access')
def open_access(message):
    user_id = message.from_user.id
    if 1:
        pass
    else:
        send_message_to_user(user_id, "Sorry I cant handle your request")


def handle_access_request(user_id, message):
    """If user status is awaiting email - """
    if user_data[user_id]["state"] == "awaiting_email":
        handle_email(user_id, message)
    elif user_data[user_id]["state"] == "awaiting_link":
        handle_link(user_id, message)
    else:
        client.logger.error("Unable to define state of the user")


def initiate_access_request(user_id):
    """Creates a dictionary for each user and sends an incoming message to provide an email"""
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
    file_id = is_google_document(link)
    if file_id:
        send_message_to_user(user_id, "Access will be opened shortly")
        email = user_data[user_id].get("email")
        client.share_document(file_id, email)
        del user_data[user_id]
    else:
        send_message_to_user(user_id, "Invalid link, please try again")


if __name__ == "__main__":
    bot.infinity_polling()
