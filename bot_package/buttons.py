from telebot import types
from google_access_share_bot.exceptions.exceptions import InvalidRoleError

_working_table = "Working Table"
_link_to_guide = "Link to Guide"
_open_access = "Open the access"
_change_email = "Change my email"

admin_markup = types.ReplyKeyboardMarkup(True)
user_markup = types.ReplyKeyboardMarkup(True)
biggiko_markup = types.ReplyKeyboardMarkup(True)

user_markup.row(_working_table, _link_to_guide).row(_open_access)
admin_markup.row(_working_table, _link_to_guide).row(_open_access)
biggiko_markup.add(_open_access)


def create_initial_markup(role):
    if role == "admin":
        return admin_markup
    elif role == "user":
        return user_markup
    elif role == "biggiko":
        return biggiko_markup
    else:
        raise InvalidRoleError(role)
