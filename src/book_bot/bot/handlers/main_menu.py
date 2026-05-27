from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from book_bot.bot.general import appointment2text, ask_for_registration, server_error
from book_bot.bot.keyboards.main_menu import (
    CancelAppointment,
    cancel_appointment_keyboard,
    user_profile_keyboard,
)
from book_bot.bot.middlewares import UserProfileCheckMiddleware
from book_bot.bot.states import MainMenuStates
from book_bot.models.models import AppointmentStatus, User
from book_bot.services.appointment import cancel_appointment, get_appointments
from book_bot.services.user import delete_user

router = Router()
router.message.middleware(UserProfileCheckMiddleware())


@router.message(F.text == "👤Профиль")
async def profile_settings(message: types.Message, state: FSMContext, user: User):
    await message.answer(
        "<b>👤 Ваш профиль</b>\n"
        f"Имя пользователя: {user.full_name}\n"
        f"Номер телефона: <code>{user.phone}</code>\n"
        f"Телеграм ID: <tg-spoiler>{user.tg_id}</tg-spoiler>",
        reply_markup=user_profile_keyboard(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(MainMenuStates.profile)


@router.callback_query(MainMenuStates.profile, F.data == "profile_change_phone")
async def change_phone(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await ask_for_registration(callback.message, state)


@router.callback_query(MainMenuStates.profile, F.data == "profile_delete")
async def delete_profile(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await delete_user(tg_id=callback.from_user.id)
    await callback.message.answer(
        "Профиль удален. Вы можете начать сначала используя /start",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@router.message(F.text == "📑Записи")
async def show_appointments(message: types.Message, user: User):
    appointments = await get_appointments(user_id=user.id)
    await message.answer("<b>Ваши записи:</b>", parse_mode=ParseMode.HTML)

    for appointment in appointments:
        markup = (
            cancel_appointment_keyboard(appointment.id)
            if appointment.status == AppointmentStatus.ACTIVE
            else None
        )
        await message.answer(
            appointment2text(appointment),
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )


@router.callback_query(CancelAppointment.filter())
async def cancel_appointment_handler(
    callback: types.CallbackQuery, callback_data: CancelAppointment
):
    appointment_id = callback_data.appointment_id
    appointment = await cancel_appointment(appointment_id=appointment_id)

    if not appointment:
        await server_error(callback)
        return

    await callback.answer()
    await callback.message.edit_text(
        appointment2text(appointment), parse_mode=ParseMode.HTML
    )
