import logging
from logging import Logger

from aiogram import Bot

from google_access_share_bot.bot.bot_logging.admin_logging import \
    BotAdminLoggingHandler


def setup_logger(
    logger: Logger, bot: Bot, log_chat_id: str, validation_level: int = logging.INFO
) -> None:
    """
    Set up an instance of logger class

    :param logger: Instance of Logger
    :param bot: Telegram bot
    :param author_chat_id: Chat ID to send logging messages
    :param validation_level: Logging level (e.g., logging.INFO, logging.DEBUG).
    :return: None
    """
    handler = BotAdminLoggingHandler(bot, log_chat_id)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%y-%m-%d"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(validation_level)


def singleton(cls):
    """
    should be used as decorator for class ensuring single ton pattern
    :param cls:
    :return:
    """
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
