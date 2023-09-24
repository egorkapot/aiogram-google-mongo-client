import logging
import asyncio
from aiogram import Bot


class BotUserLoggingHandler(logging.Handler):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot
        self.user_chat_id = None

    def set_chat_id(self, user_chat_id):
        self.user_chat_id = user_chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry_ = self.format(record)
        if self.user_chat_id:
            asyncio.create_task(self.async_emit(log_entry_))

    async def async_emit(self, log_entry: str) -> None:
        await self.bot.send_message(self.user_chat_id, log_entry)

