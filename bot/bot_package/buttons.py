from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           KeyboardButton, ReplyKeyboardMarkup)

from google_access_share_bot.exceptions.exceptions import InvalidRoleError


class ReplyButtons:
    open_access = KeyboardButton(text="Open the access")
    change_email = KeyboardButton(text="Change my email")
    all_links = KeyboardButton(text="All Links")
    delete_user = KeyboardButton(text="Delete User")

    @classmethod
    def admin_markup(cls):
        """
        Returns markup for admin.
        Keep in mind that all_links for admin and user are different
        :return:
        """
        return ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[[cls.open_access], [cls.all_links, cls.change_email], [cls.delete_user]]
        )

    @classmethod
    def user_markup(cls):
        """
        Returns markup for user.
        Keep in mind that all_links for admin and user are different
        :return:
        """
        return ReplyKeyboardMarkup(
            resize_keyboard=True, keyboard=[[cls.open_access], [cls.all_links, cls.change_email]]
        )

    @classmethod
    def biggiko_markup(cls):
        return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[[cls.open_access]])

    @classmethod
    def create_initial_markup(cls, role) -> ReplyKeyboardMarkup:
        """
        Creates a markup for user depending on provided role

        :param role: User's role
        :return: Instance of ReplyKeyboardMarkup
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
    web_content_table_ = InlineKeyboardButton(
        text="Web 2.0 table", callback_data="table_web_content"
    )
    web_ai_table_ = InlineKeyboardButton(
        text="Web AI table", callback_data="table_web_ai_content"
    )
    seo_content_table_ = InlineKeyboardButton(
        text="SEO table", callback_data="table_seo_content"
    )
    backup_table_ = InlineKeyboardButton(
        text="Backup table", callback_data="table_backup"
    )
    link_to_guide_ = InlineKeyboardButton(
        text="Link to Guide", callback_data="table_link_to_guide"
    )
    working_tables_markup = [web_content_table_, web_ai_table_, seo_content_table_]
    all_link_markup = [
        [web_content_table_, web_ai_table_, seo_content_table_],
        [backup_table_, link_to_guide_]
    ]
    confirm_button = InlineKeyboardButton(
        text="Confirm Selection ✅", callback_data="confirm"
    )
    skip_button = InlineKeyboardButton(text="Skip ⏩", callback_data="skip")

    @classmethod
    def admin_markup(cls) -> InlineKeyboardMarkup:
        """
        Returns inline markup for admin

        :return: Instance of InlineKeyboardMarkup
        """
        return InlineKeyboardMarkup(inline_keyboard=cls.all_link_markup)

    @classmethod
    def user_markup(cls) -> InlineKeyboardMarkup:
        """
        Returns inline markup for user

        :return:  Instance of inline keyboard markup
        """
        return InlineKeyboardMarkup(inline_keyboard=[[cls.link_to_guide_]])

    @classmethod
    def generate_all_link_markup(cls, role) -> InlineKeyboardMarkup:
        """
        Creates a markup for user depending on provided role

        :param role: User's role
        :return: Instance of ReplyKeyboardMarkup
        """
        if role == "admin":
            return cls.admin_markup()
        elif role == "user":
            return cls.user_markup()
        else:
            raise InvalidRoleError(role)

    @staticmethod
    def generate_markup(
        markup: list[list[InlineKeyboardButton]],
    ) -> InlineKeyboardMarkup:
        """
        Generates the markup for user
        :param markup: List of buttons to provide
        :return: Inline keyboard markup
        """
        return InlineKeyboardMarkup(inline_keyboard=markup)

    @staticmethod
    def generate_confirmation_markup(user_id: int) -> InlineKeyboardMarkup:
        """
        Generates the markup for author with the callback buttons where to accept the registration or not

        :param user_id: ID of user to send to callback handler
        :return: Markup of keyboard buttons
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
        _biggiko_role = InlineKeyboardButton(
            text="biggiko", callback_data=f"role_biggiko_{user_id}"
        )
        _user_role = InlineKeyboardButton(
            text="user", callback_data=f"role_user_{user_id}"
        )
        _admin_role = InlineKeyboardButton(
            text="admin", callback_data=f"role_admin_{user_id}"
        )
        role_markup = InlineKeyboardMarkup(
            inline_keyboard=[[_biggiko_role, _user_role, _admin_role]]
        )
        return role_markup

    @staticmethod
    def create_markup_excluding(callback_data, markup: InlineKeyboardMarkup):
        new_markup = []
        for row in markup.inline_keyboard:
            new_row = [
                button for button in row if button.callback_data != callback_data
            ]
            if new_row:
                new_markup.append(new_row)
        return InlineKeyboardMarkup(inline_keyboard=new_markup)


reply_buttons = ReplyButtons()
inline_buttons = InlineButtons()
