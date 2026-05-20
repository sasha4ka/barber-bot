import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from book_bot.bot.keyboards.appointment import get_confirm_keyboard, get_slots_keyboard
from book_bot.bot.middlewares import UserProfileCheckMiddleware
from book_bot.bot.states import CreateAppointmentStates
from book_bot.models.models import Slot, User
from book_bot.services.appointment import create_appointment
from book_bot.services.slot import get_slot, get_slots

router = Router()
router.message.middleware(UserProfileCheckMiddleware())


@router.message(F.text == "📖Записаться")
async def schedule(message: types.Message, state: FSMContext, user: User):
    await state.set_state(CreateAppointmentStates.select_slot)
    await state.update_data(user_id=user.id)
    target_date = datetime.datetime.now().date()
    slots: list[Slot] = await get_slots(target_date=target_date)

    keyboard = get_slots_keyboard(slots)
    await message.answer("Выберите время записи:", reply_markup=keyboard)


@router.callback_query(CreateAppointmentStates.select_slot)
async def choose_slot(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(CreateAppointmentStates.comfirm)
    try:
        slot_id = int(callback.data)
    except ValueError:
        await callback.answer("Серверная ошибка... Попробуйте еще раз")
        return
    await state.update_data(slot_id=slot_id)

    slot = await get_slot(slot_id)
    if slot is None:
        await callback.answer("Серверная ошибка... Попробуйте еще раз")
        return

    time = slot.time_start

    await callback.message.edit_text(
        f"Вы подтверждаете запись на {time:%H:%M}?", reply_markup=get_confirm_keyboard()
    )


@router.callback_query(CreateAppointmentStates.comfirm, F.data == "confirm")
async def confirm_appointment(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    slot_id = data["slot_id"]
    user_id = data["user_id"]

    appointment = await create_appointment(user_id, slot_id)
    if not appointment:
        await callback.answer("Слот занят или не существует!")
        return

    slot = await get_slot(slot_id)
    if not slot:
        await callback.answer("Внутренняя ошибка")
        return
    time = slot.time_start

    await state.clear()
    await callback.message.edit_text(f"Вы успешно записаны на {time:%H:%M}")


@router.callback_query(CreateAppointmentStates.comfirm, F.data == "cancel")
async def cancel_appointment(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Вы отменили запись")
