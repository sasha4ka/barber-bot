from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


class CancelAppointment(CallbackData, prefix="cancel-appointment"):
    appointment_id: int


def main_menu_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    if is_admin:
        builder.row(
            KeyboardButton(text="✏️Записаться"),
            KeyboardButton(text="📑Записи"),
            KeyboardButton(text="👤Профиль"),
            KeyboardButton(text="⚙️Админ-панель"),
        )
    else:
        builder.row(
            KeyboardButton(text="✏️Записаться"),
            KeyboardButton(text="📑Записи"),
            KeyboardButton(text="👤Профиль"),
        )

    return builder.as_markup(resize_keyboard=True)


def user_profile_keyboard() -> InlineKeyboardMarkup:
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


def cancel_appointment_keyboard(appointment_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(
            text="❌Отменить",
            callback_data=CancelAppointment(appointment_id=appointment_id).pack(),
        )
    )
    return builder.as_markup()
