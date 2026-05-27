from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="✅", callback_data="confirm"))
    builder.add(InlineKeyboardButton(text="❌", callback_data="cancel"))

    return builder.as_markup()
