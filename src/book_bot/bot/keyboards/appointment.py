from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from book_bot.models import Master, Slot


class MasterSelectionResult(CallbackData, prefix="select-master"):
    master_id: int
    canceled: bool


class SlotSelectionResult(CallbackData, prefix="select-slot"):
    slot_id: int
    canceled: bool


def get_master_keyboard(masters: list[Master]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for master in masters:
        builder.add(
            InlineKeyboardButton(
                text=master.full_name,
                callback_data=MasterSelectionResult(
                    master_id=master.id, canceled=False
                ).pack(),
            )
        )
    builder.add(
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=MasterSelectionResult(master_id=0, canceled=True).pack(),
        )
    )

    builder.adjust(1)
    return builder.as_markup()


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
