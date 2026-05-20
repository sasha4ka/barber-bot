from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from book_bot.models.models import Slot


def get_slots_keyboard(slots: list[Slot]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for slot in slots:
        is_free = "Занят" if slot.is_booked else "Свободен"
        label = f"{slot.time_start:%H:%M} - {is_free}"
        builder.add(InlineKeyboardButton(text=label, callback_data=f"{slot.id}"))

    builder.adjust(1)
    return builder.as_markup()


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="✅", callback_data="confirm"))
    builder.add(InlineKeyboardButton(text="❌", callback_data="cancel"))

    return builder.as_markup()
