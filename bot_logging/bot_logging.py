import logging

from telebot import TeleBot


class BotLoggingHandler(logging.Handler):
    def __init__(self, bot: TeleBot, chat_id: str):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry = self.format(record)
        self.bot.send_message(self.chat_id, log_entry)
