import datetime
from enum import Enum
from typing import List, Optional

from core_shared.exc import SlotAlreadyBookedException, SlotNotFoundException
from core_shared.models import Appointment, AppointmentStatus, Slot
from core_shared.services.notification import get_notification_service
from sqlalchemy import between, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class ActionBy(str, Enum):
    CLIENT = "client"
    MASTER = "master"


async def create_appointment(
    user_id: int, slot_id: int, session: AsyncSession
) -> Appointment:
    slot_query = select(Slot).where(Slot.id == slot_id).with_for_update()
    slot_result = await session.execute(slot_query)
    slot = slot_result.scalar_one_or_none()

    if not slot:
        raise SlotNotFoundException

    if slot.is_booked:
        raise SlotAlreadyBookedException

    appointment = Appointment(
        user_id=user_id, slot_id=slot_id, status=AppointmentStatus.ACTIVE
    )
    session.add(appointment)
    slot.is_booked = True

    await session.flush()
    await session.refresh(appointment)

    return appointment


async def complete_appointment(
    appointment_id: int, session: AsyncSession
) -> Optional[Appointment]:
    query = (
        select(Appointment)
        .join(Appointment.slot)
        .join(Appointment.user)
        .where(Appointment.id == appointment_id)
        .options(joinedload(Appointment.slot), joinedload(Appointment.user))
    )
    result = await session.execute(query)
    appointment = result.scalar_one_or_none()
    if not appointment:
        return

    appointment.status = AppointmentStatus.COMPLETED
    await session.flush()
    await session.refresh(appointment)
    notifier = get_notification_service()
    await notifier.send_notification(
        appointment.user.tg_id,
        f"✅Ваша запись на {appointment.slot.time_start:%H:%M} закрыта",
    )
    return appointment


async def cancel_appointment(
    *, appointment_id: int, by: ActionBy = ActionBy.CLIENT, session: AsyncSession
) -> Optional[Appointment]:
    query = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(
            joinedload(Appointment.slot).joinedload(Slot.master),
            joinedload(Appointment.user),
        )
    )
    result = await session.execute(query)
    appointment = result.scalar_one_or_none()
    if not appointment:
        return

    appointment.slot.is_booked = False
    appointment.status = AppointmentStatus.CANCELLED

    await session.flush()
    await session.refresh(appointment)

    notifier = get_notification_service()
    if by == ActionBy.MASTER:
        await notifier.send_notification(
            appointment.user.tg_id,
            f"Ваша запись на {appointment.slot.time_start:%H:%M} была отменена администратором",
        )
    elif by == ActionBy.CLIENT:
        if appointment.slot.master.tg_id:
            await notifier.send_notification(
                appointment.slot.master.tg_id,
                (
                    f"Пользователь {appointment.user.full_name} #{appointment.user.id} "
                    f"отменил запись на {appointment.slot.time_start:%H:%M} #{appointment_id}"
                ),
            )

    return appointment


async def get_appointments(
    *,
    user_id: Optional[int] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    master_id: Optional[int] = None,
    only_active: bool = True,
    session: AsyncSession,
) -> List[Appointment]:
    """Returns list of appointments. If user_id specified: return user's appointments. \
If start_date end end_date (By default equal to start_date) specified, \
returns appointments in between start_date and end_date. If master_id \
specified, returns appointments to specified master"""
    if end_date and not start_date:
        return []

    if start_date and not end_date:
        end_date = start_date

    query = (
        select(Appointment)
        .join(Appointment.slot)
        .options(joinedload(Appointment.slot).joinedload(Slot.master))
        .order_by(Slot.date, Slot.time_start)
    )

    if start_date:
        query = query.where(between(Slot.date, start_date, end_date))

    if user_id:
        query = query.where(Appointment.user_id == user_id)

    if only_active:
        query = query.where(Appointment.status == AppointmentStatus.ACTIVE)

    if master_id:
        query = query.where(Slot.master_id == master_id)

    results = await session.execute(query)
    return list(results.scalars().all())


async def get_appointment(
    *, appointment_id: int, session: AsyncSession
) -> Optional[Appointment]:
    query = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(
            joinedload(Appointment.slot).joinedload(Slot.master),
            joinedload(Appointment.user),
        )
    )
    return (await session.execute(query)).scalar_one_or_none()


async def reschedule_appointment(
    *,
    appointment_id: int,
    new_slot_id: int,
    by: ActionBy = ActionBy.CLIENT,
    session: AsyncSession,
) -> Optional[Appointment]:
    appointment_query = (
        select(Appointment)
        .where(Appointment.id == appointment_id)
        .options(
            joinedload(Appointment.slot).joinedload(Slot.master),
            joinedload(Appointment.user),
        )
    )
    appointment = (await session.execute(appointment_query)).scalar_one_or_none()
    if not appointment:
        return None
    old_slot = appointment.slot

    query = (
        select(Slot)
        .where(Slot.id == new_slot_id)
        .with_for_update(of=Slot)
        .options(joinedload(Slot.master))
    )
    new_slot = (await session.execute(query)).scalar_one_or_none()
    if not new_slot:
        raise SlotNotFoundException

    if new_slot.is_booked:
        raise SlotAlreadyBookedException

    appointment.slot_id = new_slot_id
    old_slot.is_booked = False
    new_slot.is_booked = True

    await session.flush()
    await session.refresh(appointment)

    notifier = get_notification_service()

    if by == ActionBy.MASTER:
        await notifier.send_notification(
            appointment.user.tg_id,
            (
                f"Ваша запись на {old_slot.time_start:%H:%M} была перенесена "
                f"на {appointment.slot.time_start:%H:%M} администратором"
            ),
        )
    elif by == ActionBy.CLIENT and old_slot.master.tg_id:
        text = (
            (
                f"Пользователь {appointment.user.full_name} #{appointment.user.id} "
                f"перенес запись #{appointment_id} с {old_slot.time_start:%H:%M} "
                f"на {appointment.slot.time_start:%H:%M}"
            )
            if old_slot.master_id == new_slot.master_id
            else (
                f"Пользователь {appointment.user.full_name} #{appointment.user.id} "
                f"перенес запись #{appointment_id} на {old_slot.time_start:%H:%M} "
                f"на другого мастера"
            )
        )
        await notifier.send_notification(old_slot.master.tg_id, text)

    return appointment
