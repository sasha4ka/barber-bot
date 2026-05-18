from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext

from book_bot.bot.general import ask_for_registration
from book_bot.bot.keyboards.main import get_profile_keyboard
from book_bot.bot.middlewares import UserProfileCheckMiddleware
from book_bot.models.models import User
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


@router.callback_query(F.data == "profile_change_phone")
async def change_phone(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await ask_for_registration(callback.message, state)


@router.callback_query(F.data == "profile_delete")
async def delete_profile(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await delete_user(tg_id=callback.from_user.id)
    await callback.message.answer(
        "Профиль удален. Вы можете начать сначала используя /start",
        reply_markup=types.ReplyKeyboardRemove(),
    )
