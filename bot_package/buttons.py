
from google_access_share_bot.exceptions.exceptions import InvalidRoleError
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
_web_content_table = KeyboardButton(text="Web 2.0 table")
_web_ai_table = KeyboardButton(text="Web AI table")
_seo_content_table = KeyboardButton(text="SEO table")
_backup_table = KeyboardButton(text="Backup table")
_link_to_guide = KeyboardButton(text="Link to Guide")
_open_access = KeyboardButton(text="Open the access")
_change_email = KeyboardButton(text="Change my email")


admin_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=[
        [_web_content_table, _web_ai_table, _seo_content_table],
        [_backup_table, _link_to_guide],
        [_open_access]
    ]
)
user_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=[
        [_web_content_table, _link_to_guide], [_open_access]
    ]
)
biggiko_markup = ReplyKeyboardMarkup(
    resize_keyboard=True, keyboard=[[_open_access]]
)


def generate_confirmation_markup(user_id: int):
    """
    Generates the markup for author with the callback buttons if to accept the registration or not

    :param user_id: id of user to send to callback handler
    :return: markup of keyboard buttons
    """
    _yes = InlineKeyboardButton(text="✅", callback_data=f"approve_{user_id}")
    _no = InlineKeyboardButton(text="⛔", callback_data=f"deny_{user_id}")
    confirmation_markup = InlineKeyboardMarkup(inline_keyboard=[[_yes, _no]])
    return confirmation_markup


def generate_user_role(user_id: int):
    """
    Generates the markup for author with the callback buttons to ask which role to set to user

    :param user_id: id of user to send to callback handler
    :return: markup of keyboard buttons
    """
    _biggiko_role = InlineKeyboardButton(text="biggiko", callback_data=f"role_biggiko_{user_id}")
    _user_role = InlineKeyboardButton(text="user", callback_data=f"role_user_{user_id}")
    _admin_role = InlineKeyboardButton(text="admin", callback_data=f"role_admin_{user_id}")
    role_markup = InlineKeyboardMarkup(inline_keyboard=[[_biggiko_role, _user_role, _admin_role]])
    return role_markup


def create_initial_markup(role):
    if role == "admin":
        return admin_markup
    elif role == "user":
        return user_markup
    elif role == "biggiko":
        return biggiko_markup
    else:
        raise InvalidRoleError(role)
