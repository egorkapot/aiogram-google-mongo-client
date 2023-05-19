import telebot
from telebot import types
from google.oauth2 import service_account
from googleapiclient import discovery, errors
import base64
from email.mime.text import MIMEText
import os
# bot.polling(none_stop=True, interval=0)

bot_token = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    name_1 = types.KeyboardButton('Андрюха')
    name_2 = types.KeyboardButton('Егор')
    markup.add(name_1, name_2)
    bot.send_message(message.from_user.id, 'Choose your fighter', reply_markup=markup)



@bot.message_handler(content_types=['text'])
def choose_fighter(message):
    if message.text == 'Андрюха':
        bot.send_message('Едет в Варшаву')
    elif message.text == 'Егор':
        bot.send_message('Тоже гонит в Варшаву')
    else:
        bot.send_message('Fighter was not chosen')

# @staticmethod
# @bot.message_handler(content_types=['text'])
# def start(self, message):
#     # self.button_message(message)
#     if message.text == 'start' or message.text == '/start{}'.format(bot_token):
#         bot.send_message(message.chat.id, 'Please click on a button to start', reply_markup=self.markup)
#     else:
#         bot.send_message(message.chat.id, 'Some issues', reply_markup=self.markup)

# @bot.message_handler(content_types='text')
# def message_reply(self, message):
#     if message.text=='Start':
#         bot.send_message(message.chat.id, 'Session has been started')
#     else:
#         bot.send_message('No start button defined')




if __name__ == '__main__':
    bot.infinity_polling()



