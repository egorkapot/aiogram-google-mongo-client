
from google_access_share_bot.exceptions.exceptions import InvalidRoleError
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class ReplyButtons:
    _web_content_table = KeyboardButton(text="Web 2.0 table")
    _web_ai_table = KeyboardButton(text="Web AI table")
    _seo_content_table = KeyboardButton(text="SEO table")
    _backup_table = KeyboardButton(text="Backup table")
    _link_to_guide = KeyboardButton(text="Link to Guide")
    _open_access = KeyboardButton(text="Open the access")
    _change_email = KeyboardButton(text="Change my email")
    table_link_markup = [_web_content_table, _web_ai_table, _seo_content_table]

    @classmethod
    def admin_markup(cls):
        return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            cls.table_link_markup,
            [cls._backup_table, cls._link_to_guide],
            [cls._open_access]
            ]
                                    )

    @classmethod
    def user_markup(cls):
        return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [cls._web_content_table, cls._link_to_guide], [cls._open_access]
        ]
                                   )

    @classmethod
    def biggiko_markup(cls):
        return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
            [cls._open_access]
        ]
                                   )

    @classmethod
    def create_initial_markup(cls, role) -> ReplyKeyboardMarkup:
        """
        Creates a markup for user depending on provided role
        :param role: user's role
        :return: markup of keyboard buttons
        """
        if role == "admin":
            return cls.admin_markup()
        elif role == "user":
            return cls.user_markup()
        elif role == "biggiko":
            return cls.biggiko_markup()
        else:
            raise InvalidRoleError(role)


class InlineButtons:
    web_content_table_ = InlineKeyboardButton(text="Web 2.0 table", callback_data="table_web_content")
    web_ai_table_ = InlineKeyboardButton(text="Web AI table", callback_data="table_web_ai_content")
    seo_content_table_ = InlineKeyboardButton(text="SEO table", callback_data="table_seo_content")
    table_link_markup = [web_content_table_, web_ai_table_, seo_content_table_]
    confirm_button = InlineKeyboardButton(text="Confirm Selection ✅", callback_data="confirm")
    skip_button = InlineKeyboardButton(text="Skip ⏩", callback_data="skip")

    @staticmethod
    def generate_markup(markup: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
        """
        Generates the markup for user
        :param markup: List of buttons to provide
        :return: Inline keyboard markup
        """
        return InlineKeyboardMarkup(inline_keyboard=markup)

    @staticmethod
    def generate_confirmation_markup(user_id: int) -> InlineKeyboardMarkup:
        """
        Generates the markup for author with the callback buttons if to accept the registration or not

        :param user_id: id of user to send to callback handler
        :return: markup of keyboard buttons
        """
        _yes = InlineKeyboardButton(text="✅", callback_data=f"approve_{user_id}")
        _no = InlineKeyboardButton(text="⛔", callback_data=f"deny_{user_id}")
        confirmation_markup = InlineKeyboardMarkup(inline_keyboard=[[_yes, _no]])
        return confirmation_markup

    @staticmethod
    def generate_user_role(user_id: int) -> InlineKeyboardMarkup:
        """
        Generates the markup with the callback buttons to ask which role to set to user

        :param user_id: id of user to send to callback handler
        :return: markup of keyboard buttons
        """
        _biggiko_role = InlineKeyboardButton(text="biggiko", callback_data=f"role_biggiko_{user_id}")
        _user_role = InlineKeyboardButton(text="user", callback_data=f"role_user_{user_id}")
        _admin_role = InlineKeyboardButton(text="admin", callback_data=f"role_admin_{user_id}")
        role_markup = InlineKeyboardMarkup(inline_keyboard=[[_biggiko_role, _user_role, _admin_role]])
        return role_markup

    @staticmethod
    def create_markup_excluding(callback_data, markup: InlineKeyboardMarkup):
        new_markup = []
        for row in markup.inline_keyboard:
            new_row = [button for button in row if button.callback_data != callback_data]
            if new_row:
                new_markup.append(new_row)
        return InlineKeyboardMarkup(inline_keyboard=new_markup)


reply_buttons = ReplyButtons()
inline_buttons = InlineButtons()


