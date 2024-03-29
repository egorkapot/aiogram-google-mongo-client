import asyncio
import logging

from aiogram import Bot


class BotAdminLoggingHandler(logging.Handler):
    def __init__(self, bot: Bot, log_chat_id):
        super().__init__()
        self.bot = bot
        self.log_chat_id = log_chat_id

    def emit(self, record: logging.LogRecord) -> None:
        log_entry_ = self.format(record)
        asyncio.create_task(self.async_emit(log_entry_))

    async def async_emit(self, log_entry: str) -> None:
        await self.bot.send_message(self.log_chat_id, log_entry)
