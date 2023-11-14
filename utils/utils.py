from google_access_share_bot.bot_logging.admin_logging import \
    BotAdminLoggingHandler
import logging
from logging import Logger
from aiogram import Bot


def setup_logger(logger: Logger, bot: Bot, author_chat_id: str) -> None:
    """
    Set up an instance of logger class

    :param logger: instance of Logger
    :param bot: telegram bot
    :param author_chat_id: chat_id to send messages
    :return: None
    """
    handler = BotAdminLoggingHandler(bot, author_chat_id)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%y-%m-%d"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


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

