import logging

from telebot import TeleBot


class BotUserLoggingHandler(logging.Handler):
    def __init__(self, bot: TeleBot):
        super().__init__()
        self.bot = bot
        self.user_chat_id = None

    def set_chat_id(self, user_chat_id):
        self.user_chat_id = user_chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        if self.user_chat_id:
            self.bot.send_message(self.user_chat_id, log_entry)
