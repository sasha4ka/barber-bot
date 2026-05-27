from aiogram import types
from aiogram.fsm.context import FSMContext

from book_bot.bot.keyboards.register_user import get_ask_phone_keyboard
from book_bot.bot.states import RegistrationStates
from book_bot.models import Appointment, AppointmentStatus


async def ask_for_registration(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        "Для заполнения профиля укажите свой контакт",
        reply_markup=get_ask_phone_keyboard(),
    )


def appointment2text(appointment: Appointment) -> str:
    text_status = {
        AppointmentStatus.CANCELLED: "❌Отменена",
        AppointmentStatus.ACTIVE: "⏳Ожидается",
        AppointmentStatus.COMPLETED: "✅Закрыта",
    }
    return (
        f"👤 Мастер: {appointment.slot.master.full_name}\n"
        f"📅 Дата: {appointment.slot.date:%d.%m.%Y}\n"
        f"🕒 Время: {appointment.slot.time_start:%H:%M}\n"
        f"ℹ️ Статус: {text_status[appointment.status]}"
    )
