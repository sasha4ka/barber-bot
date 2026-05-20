import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from book_bot.bot.general import ask_for_registration
from book_bot.bot.keyboards import (
    get_profile_keyboard,
)
from book_bot.bot.middlewares import UserProfileCheckMiddleware
from book_bot.bot.states import MainMenuStates
from book_bot.core.settings import settings
from book_bot.models.models import AppointmentStatus, User
from book_bot.services.appointment import get_appointments
from book_bot.services.slot import generate_slots_for_date
from book_bot.services.user import delete_user

router = Router()
router.message.middleware(UserProfileCheckMiddleware())


@router.message(F.text == "👤Профиль")
async def profile_settings(message: types.Message, state: FSMContext, user: User):
    await message.answer(
        "<b>👤 Ваш профиль</b>"
        f"Имя пользователя: {user.full_name}\n"
        f"Номер телефона: <code>{user.phone}</code>\n"
        f"Телеграм ID: <tg-spoiler>{user.tg_id}</tg-spoiler>",
        reply_markup=get_profile_keyboard(),
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
    appointments = await get_appointments(
        user_id=user.id, start_date=datetime.datetime.now().date()
    )
    text_status = {
        AppointmentStatus.CANCELLED: "❌Отменена",
        AppointmentStatus.ACTIVE: "⏳Ожидается",
        AppointmentStatus.COMPLETED: "✅Закрыта",
    }
    text = "\n".join(
        [
            f"{app.slot.time_start:%H:%M} - {text_status[app.status]}"
            for app in appointments
        ]
    )
    await message.answer(
        "Ваши записи на сегодня:\n\n" + text, parse_mode=ParseMode.HTML
    )


@router.message(F.text == "/gen-slots")
async def DEBUG_generate_slots(message: types.Message):
    if not settings.DEBUG:
        return
    target_date = datetime.datetime.now().date()
    work_start = datetime.time(10)
    work_end = datetime.time(18)
    await generate_slots_for_date(
        target_date=target_date, work_start=work_start, work_end=work_end
    )
    await message.reply("Successful generated")
