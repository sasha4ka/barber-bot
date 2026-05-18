from aiogram import types
from aiogram.fsm.context import FSMContext

from book_bot.bot.keyboards import get_ask_phone_keyboard
from book_bot.bot.states import RegistrationStates


async def ask_for_registration(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationStates.waiting_for_phone)
    await message.answer(
        "Для заполнения профиля укажите свой контакт",
        reply_markup=get_ask_phone_keyboard(),
    )
