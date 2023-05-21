import os
import telebot
from dotenv import load_dotenv
from telebot import types
from emails.emails import get_emails_list

load_dotenv()
bot_token = os.environ.get("BOT_TOKEN")
author_chat_id = os.environ.get("AUTHOR_CHAT_ID")
bot = telebot.TeleBot(bot_token)
list_of_emails = get_emails_list()


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
    if message.text == "Open the access":
        bot.send_message(message.from_user.id, "Not implemented yet")
    elif message.text == "Working Table":
        bot.send_message(message.from_user.id, os.environ.get("TABLE_LINK"))
    elif message.text == "Link to Guide":
        bot.send_message(message.from_user.id, os.environ.get("GUIDE_LINK"))


if __name__ == "__main__":
    bot.infinity_polling()
