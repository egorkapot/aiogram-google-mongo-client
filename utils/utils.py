import re
from google_access_share_bot.bot_logging.admin_logging import \
    BotAdminLoggingHandler
import logging
from logging import Logger
from aiogram import Bot


def is_google_document(link):
    """Validates that the link is a document"""
    pattern = r"(https://docs.google.com/document/d/)([a-zA-Z0-9-_]+)"
    return bool(re.match(pattern, link))


def is_google_spreadsheet(link):
    """Validates that the link is spreadsheet"""
    pattern = r"(https://docs.google.com/spreadsheets/d/)([a-zA-Z0-9-_]+)"
    return bool(re.match(pattern, link))


def generate_id(link):
    """Generates the id of the file from link to open the access"""
    pattern = r"(https://docs.google.com/[^/]+/d/)([a-zA-Z0-9-_]+)"
    match = re.match(pattern, link)
    if match:
        file_id = match.group(2)
        return file_id


def get_grid_range(sheet_id, start_row, end_row, start_col, end_col):
    """Returns a GridRange object for batch updates."""
    return {
        "sheetId": sheet_id,
        "startRowIndex": start_row,
        "endRowIndex": end_row,
        "startColumnIndex": start_col,
        "endColumnIndex": end_col,
    }


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


def is_google_email(email: str) -> bool:
    """
    Validates if the provided email is a Google email.

    :param email: email to validate
    :return: bool
    """
    email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    if not email_pattern.fullmatch(email):
        return False

    domain = email.split('@')[1].lower()

    # Check if the domain is gmail.com or your custom Google Workspace domain
    return domain in ["gmail.com", "biggiko.com", "alreadymedia.com"]


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

