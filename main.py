import os
import telebot
from dotenv import load_dotenv
from telebot import types
from emails.emails import get_emails_list

load_dotenv()


bot_token = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)
list_of_emails = get_emails_list()


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    open_access = types.KeyboardButton("Открыть доступ")
    link_to_table = types.KeyboardButton("Ссылка на рабочую таблицу")
    link_to_guide = types.KeyboardButton("Ссылка на гайд")
    markup.add(open_access, link_to_table, link_to_guide)
    bot.send_message(message.from_user.id, "Выбери что тебе нужно", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def message_handling(message):
    if message.text == "Открыть доступ":
        bot.send_message(message.from_user.id, "Not implemented yet")
    elif message.text == "Ссылка на рабочую таблицу":
        bot.send_message(message.from_user.id, os.environ.get("TABLE_LINK"))
    elif message.text == "Ссылка на гайд":
        bot.send_message(message.from_user.id, os.environ.get("GUIDE_LINK"))


if __name__ == "__main__":
    bot.infinity_polling()
