from enum import Enum

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    KeyboardButtonRequestUsers,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class AdminPanelButtons(str, Enum):
    users = "👤Пользователи"
    records = "📑Записи"
    generate_slots = "🗓️Сгенерировать слоты"
    masters = "👤Мастера"
    back = "⬅️Назад"


def admin_panel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.row(
        KeyboardButton(text=AdminPanelButtons.users.value),
        KeyboardButton(text=AdminPanelButtons.records.value),
        KeyboardButton(text=AdminPanelButtons.masters.value),
        KeyboardButton(text=AdminPanelButtons.generate_slots.value),
    )
    builder.row(KeyboardButton(text=AdminPanelButtons.back.value))

    return builder.as_markup(resize_keyboard=True)


def create_master_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Создать профиль мастера", callback_data="add_master")
    )
    return builder.as_markup(resize_keyboard=True)


def get_master_profile_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    builder.add(
        KeyboardButton(
            text="Поделиться контактом",
            request_users=KeyboardButtonRequestUsers(request_id=1, user_is_bot=False),
        ),
        KeyboardButton(text="Не привязывать профиль"),
    )
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
