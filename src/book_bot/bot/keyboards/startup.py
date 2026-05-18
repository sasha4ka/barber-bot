from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_ask_phone_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text="Поделиться номером телефона", request_contact=True)
    )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
