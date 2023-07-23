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

@bot.message_handler(commands=["cleantable"])
def clean_working_table(message):
    user_id = message.from_user.id
    if user_id in admin_chat_id:
        send_message_to_user(user_id, "Authenticated, now provide link to table")
    else:
        send_message_to_user(user_id, "You are not the admin")
        client.logger.error(f"{user_id} tried to access cleantable")

@bot.message_handler(commands=['me'])
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


@bot.message_handler(func=lambda message: message.text == 'Working Table')
def send_link_to_working_table(message):
    user_id = message.from_user.id
    send_message_to_user(user_id, os.environ.get("TABLE_LINK"))


@bot.message_handler(func=lambda message: message.text == 'Link to Guide')
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
