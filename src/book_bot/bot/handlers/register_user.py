from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from book_bot.bot.general import ask_for_registration
from book_bot.bot.keyboards.main_menu import main_menu_keyboard
from book_bot.bot.states import RegistrationStates
from book_bot.core.exceptions import InternalError
from book_bot.services.user import create_user, get_user, modify_user

router = Router()


@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    if not message.from_user:
        raise InternalError

    if user := await get_user(tg_id=message.from_user.id):
        await message.answer(
            f"С возвращением, {user.full_name}",
            reply_markup=main_menu_keyboard(is_admin=user.is_admin),
        )
        return

    await message.answer("Приветствую! Это бот для записи в салон красоты")
    await ask_for_registration(message, state)


@router.message(F.contact, RegistrationStates.waiting_for_phone)
async def register_user(message: types.Message, state: FSMContext):
    if not message.from_user or not message.contact:
        raise InternalError

    tg_id = message.from_user.id
    full_name = message.from_user.full_name
    phone_number = message.contact.phone_number

    if (user := await get_user(tg_id=tg_id)) is not None:
        await modify_user(user=user, full_name=full_name, phone_number=phone_number)
    else:
        user = await create_user(
            tg_id=tg_id, full_name=full_name, phone_number=phone_number
        )

    if not user:
        raise InternalError

    await state.clear()
    await message.answer(
        "Профиль заполнен!",
        reply_markup=main_menu_keyboard(is_admin=user.is_admin),
    )


@router.message(RegistrationStates.waiting_for_phone)
async def expected_contact(message: types.Message, state: FSMContext):
    await message.reply(
        "Для завершения регистрации профиля необходимо поделиться вашим номером телефона"
    )
