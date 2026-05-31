import datetime

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from core_shared import AsyncSession
from core_shared.models import User
from core_shared.services.appointment import create_appointment
from core_shared.services.master import get_master, get_masters
from core_shared.services.slot import get_slot, get_slots

from bot.core.database import db
from bot.core.exceptions import InternalError
from bot.keyboards.appointment import (
    MasterSelectionResult,
    SlotSelectionResult,
    get_master_keyboard,
    get_slots_keyboard,
)
from bot.keyboards.general import confirm_keyboard
from bot.middlewares import UserProfileCheckMiddleware
from bot.states import CreateAppointmentStates

router = Router()
router.message.middleware(UserProfileCheckMiddleware(db))


@router.message(F.text == "✏️Записаться")
async def schedule(
    message: types.Message, state: FSMContext, user: User, session: AsyncSession
):
    await state.update_data(user_id=user.id)

    masters = await get_masters(session=session)
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
    session: AsyncSession,
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    master_id = callback_data.master_id
    await state.update_data(master_id=master_id)

    master = await get_master(master_id=master_id, session=session)

    if master is None:
        raise InternalError

    target_date = datetime.datetime.now().date()
    slots = await get_slots(
        start_date=target_date, master_id=master_id, session=session
    )
    keyboard = get_slots_keyboard(slots)

    await callback.message.edit_text("Выберите время записи:", reply_markup=keyboard)
    await state.set_state(CreateAppointmentStates.select_slot)


@router.callback_query(
    CreateAppointmentStates.select_slot, SlotSelectionResult.filter(~F.canceled)
)
async def choose_slot(
    callback: types.CallbackQuery,
    callback_data: SlotSelectionResult,
    state: FSMContext,
    session: AsyncSession,
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    slot_id = callback_data.slot_id
    await state.update_data(slot_id=slot_id)

    slot = await get_slot(slot_id, session=session)

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
async def confirm_appointment(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    data = await state.get_data()

    slot_id = data["slot_id"]
    user_id = data["user_id"]

    slot = await get_slot(slot_id, session=session)
    if not slot:
        raise InternalError

    if slot.is_booked:
        await callback.answer("Слот уже занят!")
        return

    appointment = await create_appointment(user_id, slot_id, session=session)
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
