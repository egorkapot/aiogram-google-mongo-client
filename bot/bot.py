from aiogram import Bot

from google_access_share_bot.settings import settings

bot_token = settings.get_bot_token().get_secret_value()
bot = Bot(bot_token)
