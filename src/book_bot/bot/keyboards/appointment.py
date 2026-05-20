from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from book_bot.models.models import Slot


class SlotSelectionResult(CallbackData, prefix="select-slot"):
    slot_id: int
    canceled: bool


def get_slots_keyboard(slots: list[Slot]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for slot in slots:
        is_free = "Занят" if slot.is_booked else "Свободен"
        label = f"{slot.time_start:%H:%M} - {is_free}"
        builder.add(
            InlineKeyboardButton(
                text=label,
                callback_data=SlotSelectionResult(
                    slot_id=slot.id, canceled=False
                ).pack(),
            )
        )

    builder.add(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=SlotSelectionResult(slot_id=0, canceled=True).pack(),
        )
    )

    builder.adjust(1)
    return builder.as_markup()


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="✅", callback_data="confirm"))
    builder.add(InlineKeyboardButton(text="❌", callback_data="cancel"))

    return builder.as_markup()
