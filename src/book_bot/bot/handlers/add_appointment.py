import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from book_bot.bot.keyboards.appointment import (
    MasterSelectionResult,
    SlotSelectionResult,
    get_master_keyboard,
    get_slots_keyboard,
)
from book_bot.bot.keyboards.general import confirm_keyboard
from book_bot.bot.middlewares import UserProfileCheckMiddleware
from book_bot.bot.states import CreateAppointmentStates
from book_bot.core.exceptions import InternalError
from book_bot.models import User
from book_bot.services.appointment import create_appointment
from book_bot.services.master import get_master, get_masters
from book_bot.services.slot import get_slot, get_slots

router = Router()
router.message.middleware(UserProfileCheckMiddleware())


@router.message(F.text == "✏️Записаться")
async def schedule(message: types.Message, state: FSMContext, user: User):
    await state.update_data(user_id=user.id)

    masters = await get_masters()
    keyboard = get_master_keyboard(masters)
    await message.answer(text="Выберите мастера:", reply_markup=keyboard)
    await state.set_state(CreateAppointmentStates.select_master)


@router.callback_query(
    CreateAppointmentStates.select_master, MasterSelectionResult.filter(~F.canceled)
)
async def choose_master(
    callback: types.CallbackQuery,
    callback_data: MasterSelectionResult,
    state: FSMContext,
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    master_id = callback_data.master_id
    await state.update_data(master_id=master_id)

    master = await get_master(master_id=master_id)

    if master is None:
        raise InternalError

    target_date = datetime.datetime.now().date()
    slots = await get_slots(target_date=target_date, master_id=master_id)
    keyboard = get_slots_keyboard(slots)

    await callback.message.edit_text("Выберите время записи:", reply_markup=keyboard)
    await state.set_state(CreateAppointmentStates.select_slot)


@router.callback_query(
    CreateAppointmentStates.select_slot, SlotSelectionResult.filter(~F.canceled)
)
async def choose_slot(
    callback: types.CallbackQuery, callback_data: SlotSelectionResult, state: FSMContext
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    slot_id = callback_data.slot_id
    await state.update_data(slot_id=slot_id)

    slot = await get_slot(slot_id)

    if slot is None:
        raise InternalError

    if slot.is_booked:
        await callback.answer("Слот уже занят!")
        return

    time = slot.time_start

    await callback.answer()
    await state.set_state(CreateAppointmentStates.comfirm)
    await callback.message.edit_text(
        f"Вы подтверждаете запись на {time:%H:%M}?", reply_markup=confirm_keyboard()
    )


@router.callback_query(CreateAppointmentStates.comfirm, F.data == "confirm")
async def confirm_appointment(callback: types.CallbackQuery, state: FSMContext):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    data = await state.get_data()

    slot_id = data["slot_id"]
    user_id = data["user_id"]

    slot = await get_slot(slot_id)
    if not slot:
        raise InternalError

    if slot.is_booked:
        await callback.answer("Слот уже занят!")
        return

    appointment = await create_appointment(user_id, slot_id)
    if not appointment:
        raise InternalError

    time = slot.time_start

    await state.clear()
    await callback.answer()
    await callback.message.edit_text(f"Вы успешно записаны на {time:%H:%M}")


async def cancel_appointment(callback: types.CallbackQuery, state: FSMContext):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Вы отменили запись")


router.callback_query(
    CreateAppointmentStates.select_master, MasterSelectionResult.filter(F.canceled)
)(cancel_appointment)


router.callback_query(
    CreateAppointmentStates.select_slot, SlotSelectionResult.filter(F.canceled)
)(cancel_appointment)


router.callback_query(CreateAppointmentStates.comfirm, F.data == "cancel")(
    cancel_appointment
)
