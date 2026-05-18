from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text="👤Профиль"))

    return builder.as_markup(resize_keyboard=True)


def get_profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="Изменить телефон", callback_data="profile_change_phone"
        )
    )
    builder.add(
        InlineKeyboardButton(text="❌ Удалить профиль", callback_data="profile_delete")
    )

    builder.adjust(1)
    return builder.as_markup()
