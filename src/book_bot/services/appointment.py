import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import between, select
from sqlalchemy.orm import joinedload

from book_bot.core.database import async_session
from book_bot.core.settings import settings
from book_bot.models.models import Appointment, AppointmentStatus, Slot
from book_bot.services.notification import send_notification


class CanceledBy(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"


async def create_appointment(user_id: int, slot_id: int) -> Optional[Appointment]:
    async with async_session() as session:
        slot_query = select(Slot).where(Slot.id == slot_id).with_for_update()
        slot_result = await session.execute(slot_query)
        slot = slot_result.scalar_one_or_none()

        if not slot or slot.is_booked:
            return None

        appointment = Appointment(
            user_id=user_id, slot_id=slot_id, status=AppointmentStatus.ACTIVE
        )
        session.add(appointment)
        slot.is_booked = True

        await session.commit()
        await session.refresh(appointment)

        return appointment


async def complete_appointment(appointment_id: int) -> Optional[Appointment]:
    async with async_session() as session:
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
        await session.commit()
        await session.refresh(appointment)
        await send_notification(
            appointment.user.tg_id,
            f"✅Ваша запись на {appointment.slot.time_start:%H:%M} закрыта",
        )
        return appointment


async def cancel_appointment(
    appointment_id: int, by: CanceledBy = CanceledBy.CLIENT
) -> Optional[Appointment]:
    async with async_session() as session:
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

        appointment.slot.is_booked = False
        appointment.status = AppointmentStatus.CANCELLED

        await session.commit()
        await session.refresh(appointment)

        if by == CanceledBy.ADMIN:
            await send_notification(
                appointment.user.tg_id,
                f"Ваша запись на {appointment.slot.time_start:%H:%M} была отменена администратором",
            )
        elif by == CanceledBy.CLIENT:
            await send_notification(
                settings.ADMIN_TG,
                (
                    f"Пользователь {appointment.user.full_name}#{appointment.user.id} "
                    f"отменил запись на {appointment.slot.time_start:%H:%M} номер {appointment_id}"
                ),
            )

        return appointment


async def get_appointments(
    *,
    user_id: Optional[int] = None,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
) -> List[Appointment]:
    """Returns list of appointments. If user_id specified: return user's appointments. \
If start_date end end_date (By default equal to start_date) specified, \
returns appointments in between start_date and end_date"""
    if start_date and not end_date:
        end_date = start_date
    if user_id:
        query = (
            select(Appointment)
            .where(Appointment.user_id == user_id)
            .options(joinedload(Appointment.slot))
        )
    elif start_date:
        query = (
            select(Appointment)
            .join(Appointment.slot)
            .where(between(Slot.date, start_date, end_date))
            .options(joinedload(Appointment.slot))
            .order_by(Slot.date, Slot.time_start)
        )
    elif user_id and start_date:
        query = (
            select(Appointment)
            .join(Appointment.slot)
            .where(
                between(Slot.date, start_date, end_date)
                and Appointment.user_id == user_id
            )
            .options(joinedload(Appointment.slot))
            .order_by(Slot.date, Slot.time_start)
        )
    else:
        return []

    async with async_session() as session:
        results = await session.execute(query)
        return list(results.scalars().all())
