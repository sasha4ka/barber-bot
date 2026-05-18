from typing import Optional

from sqlalchemy import select

from book_bot.core.database import async_session
from book_bot.models.models import Appointment, AppointmentStatus, Slot


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

        await session.commit()
        await session.refresh(appointment)

        return appointment


async def complete_appointment(appointment_id: int) -> Optional[Appointment]:
    async with async_session() as session:
        query = select(Appointment).where(Appointment.id == appointment_id)
        result = await session.execute(query)
        appointment = result.scalar_one_or_none()
        if not appointment:
            return

        appointment.status = AppointmentStatus.COMPLETED
        await session.commit()
        await session.refresh(appointment)
        return appointment


async def cancel_appointment(appointment_id: int) -> Optional[Appointment]:
    async with async_session() as session:
        query = select(Appointment).where(Appointment.id == appointment_id)
        result = await session.execute(query)
        appointment = result.scalar_one_or_none()
        if not appointment:
            return

        if appointment.slot:
            appointment.slot.is_booked = False

        appointment.status = AppointmentStatus.CANCELLED
        await session.commit()
        await session.refresh(appointment)
        return appointment
