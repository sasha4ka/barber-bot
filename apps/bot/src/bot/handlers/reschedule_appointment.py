import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from core_shared import AsyncSession
from core_shared.exc import SlotAlreadyBookedException, SlotNotFoundException
from core_shared.models import AppointmentStatus
from core_shared.services.appointment import (
    ActionBy,
    get_appointment,
    reschedule_appointment,
)
from core_shared.services.master import get_master, get_masters
from core_shared.services.slot import get_slot, get_slots

from bot.core.database import db
from bot.core.exceptions import InternalError
from bot.general import appointment2text
from bot.keyboards.appointment import (
    MasterSelectionResult,
    SlotSelectionResult,
    get_master_keyboard,
    select_slot_keyboard,
)
from bot.keyboards.general import confirm_keyboard
from bot.keyboards.main_menu import RescheduleAppointment, appointment_keyboard
from bot.middlewares import UserProfileCheckMiddleware
from bot.states import RescheduleAppointmentStates

router = Router()
router.message.middleware(UserProfileCheckMiddleware(db))


@router.callback_query(RescheduleAppointment.filter())
async def reschedule_appointment_handler(
    callback: types.CallbackQuery,
    callback_data: RescheduleAppointment,
    session: AsyncSession,
    state: FSMContext,
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    appointment_id = callback_data.appointment_id
    appointment = await get_appointment(appointment_id=appointment_id, session=session)

    if appointment is None:
        raise InternalError

    if appointment.status != "active":
        await callback.answer(
            text="Запись завершена или отменена, её нельзя перенести", show_alert=True
        )
        return

    await callback.message.edit_text(
        text="Выберите нового мастера:",
        reply_markup=get_master_keyboard(await get_masters(session=session)),
    )
    await state.update_data(appointment_id=appointment_id)
    await state.set_state(RescheduleAppointmentStates.select_master)


@router.callback_query(
    RescheduleAppointmentStates.select_master, MasterSelectionResult.filter(~F.canceled)
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

    master = await get_master(master_id=master_id, session=session)
    if not master:
        raise InternalError

    await state.update_data(mater_id=master_id)

    slots = await get_slots(
        start_date=datetime.datetime.now().date(), master_id=master_id, session=session
    )

    keyboard = select_slot_keyboard(slots)

    await callback.message.edit_text("Выберите время записи:", reply_markup=keyboard)
    await callback.answer()
    await state.set_state(RescheduleAppointmentStates.select_slot)


@router.callback_query(
    RescheduleAppointmentStates.select_slot, SlotSelectionResult.filter(~F.canceled)
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
    slot = await get_slot(slot_id=slot_id, session=session)
    if slot is None:
        raise InternalError

    if slot.is_booked:
        await callback.answer("Слот уже занят!", show_alert=True)
        return

    await state.update_data(slot_id=slot_id)

    time = slot.time_start

    await callback.answer()
    await callback.message.edit_text(
        f"Вы подтверждаете перенос записи на {time:%H:%M}?",
        reply_markup=confirm_keyboard(),
    )
    await state.set_state(RescheduleAppointmentStates.confirm)


@router.callback_query(RescheduleAppointmentStates.confirm, F.data == "confirm")
async def confirm_rescheduling(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    data = await state.get_data()
    appointment_id = data["appointment_id"]
    slot_id = data["slot_id"]
    slot = await get_slot(slot_id, session=session)
    appointment = await get_appointment(appointment_id=appointment_id, session=session)

    if slot is None or slot.is_booked:
        raise InternalError

    if appointment is None:
        raise InternalError

    try:
        await reschedule_appointment(
            appointment_id=appointment_id,
            new_slot_id=slot_id,
            by=ActionBy.CLIENT,
            session=session,
        )
    except (
        SlotNotFoundException,
        SlotAlreadyBookedException,
    ):
        raise InternalError

    markup = (
        appointment_keyboard(appointment_id)
        if appointment.status == AppointmentStatus.ACTIVE
        else None
    )

    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        appointment2text(appointment), parse_mode=ParseMode.HTML, reply_markup=markup
    )


async def cancel_rescheduling(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    if not callback.message or isinstance(callback.message, types.InaccessibleMessage):
        raise InternalError

    appointment_id = await state.get_value("appointment_id")
    if not appointment_id:
        raise InternalError

    appointment = await get_appointment(appointment_id=appointment_id, session=session)
    if not appointment:
        raise InternalError

    markup = (
        appointment_keyboard(appointment_id)
        if appointment.status == AppointmentStatus.ACTIVE
        else None
    )

    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        appointment2text(appointment), parse_mode=ParseMode.HTML, reply_markup=markup
    )


router.callback_query.register(
    cancel_rescheduling,
    RescheduleAppointmentStates.select_master,
    MasterSelectionResult.filter(F.canceled),
)

router.callback_query.register(
    cancel_rescheduling,
    RescheduleAppointmentStates.select_slot,
    SlotSelectionResult.filter(F.canceled),
)

router.callback_query.register(
    cancel_rescheduling, RescheduleAppointmentStates.confirm, F.data == "cancel"
)
