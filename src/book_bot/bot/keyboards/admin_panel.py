from enum import Enum

from aiogram.types import (
    KeyboardButton,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class AdminPanelButtons(str, Enum):
    users = "👤Пользователи"
    records = "📑Записи"
    generate_slots = "🗓️Сгенерировать слоты"
    back = "⬅️Назад"


def admin_panel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text=AdminPanelButtons.users.value),
        KeyboardButton(text=AdminPanelButtons.records.value),
        KeyboardButton(text=AdminPanelButtons.generate_slots.value),
    )
    builder.row(KeyboardButton(text=AdminPanelButtons.back.value))

    return builder.as_markup(resize_keyboard=True)


def ask_contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(
            text="Поделиться контактом",
            request_users=KeyboardButtonRequestUsers(request_id=1, user_is_bot=False),
        )
    )
    return builder.as_markup(resize_keyboard=True)
