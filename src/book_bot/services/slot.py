import datetime
from typing import Optional

from sqlalchemy import select

from book_bot.core.database import async_session
from book_bot.models import Slot
from book_bot.services.master import get_masters


async def generate_slots_for_date(
    *,
    target_date: datetime.date,
    work_start: datetime.time,
    work_end: datetime.time,
    slot_duration_minutes: int = 60,
    master_id: Optional[int] = None,
) -> list[Slot]:
    if master_id:
        masters = [master_id]
    else:
        masters = [master.id for master in await get_masters()]

    async with async_session() as session:
        existing_slots_query = select(Slot).where(Slot.date == target_date)
        existing_slots_result = await session.execute(existing_slots_query)
        if existing_slots_result.scalars().first():
            return []

        step = datetime.timedelta(minutes=slot_duration_minutes)
        end_datetime = datetime.datetime.combine(target_date, work_end)

        new_slots: list[Slot] = []

        for m_id in masters:
            current_datetime = datetime.datetime.combine(target_date, work_start)

            while current_datetime + step <= end_datetime:
                slot = Slot(
                    date=target_date,
                    time_start=current_datetime.time(),
                    is_booked=False,
                    master_id=m_id,
                )
                new_slots.append(slot)
                current_datetime += step

        if new_slots:
            session.add_all(new_slots)
            await session.commit()

        return new_slots


async def get_slots(
    *,
    start_date: Optional[datetime.date] = None,
    end_date: Optional[datetime.date] = None,
    master_id: Optional[int] = None,
) -> list[Slot]:
    """Returns slots.
If master_id: returns slots to specifies master
If start_date and end_date (by default equal to start_date): \
returns slots in between start_date and end_date"""
    query = select(Slot).order_by(Slot.master_id, Slot.time_start)

    if end_date and not start_date:
        return []

    if start_date and not end_date:
        end_date = start_date

    if master_id:
        query = query.where(Slot.master_id == master_id)

    if start_date:
        query = query.where(Slot.date.between(start_date, end_date))

    async with async_session() as session:
        result = await session.execute(query)
        slots = result.scalars()
        return list(slots)


async def get_slot(slot_id: int) -> Optional[Slot]:
    async with async_session() as session:
        query = select(Slot).where(Slot.id == slot_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
