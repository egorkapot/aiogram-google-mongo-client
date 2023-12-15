from aiogram import Bot

from settings import settings

bot_token = settings.get_bot_token().get_secret_value()
bot = Bot(bot_token)
