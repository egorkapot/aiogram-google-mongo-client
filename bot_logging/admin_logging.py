import logging

from telebot import TeleBot


class BotAdminLoggingHandler(logging.Handler):
    def __init__(self, bot: TeleBot, admin_chat_id):
        super().__init__()
        self.bot = bot
        self.admin_chat_id = admin_chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        self.bot.send_message(self.admin_chat_id, log_entry)
