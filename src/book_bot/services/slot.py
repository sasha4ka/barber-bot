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

    print(masters)

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
    target_date: datetime.date, master_id: Optional[int] = None
) -> list[Slot]:
    if master_id:
        query = select(Slot).where(
            Slot.date == target_date, Slot.master_id == master_id
        )
    else:
        query = select(Slot).where(Slot.date == target_date)
    async with async_session() as session:
        result = await session.execute(query)
        slots = result.scalars()
        return sorted(list(slots), key=lambda slot: slot.time_start)


async def get_slot(slot_id: int) -> Optional[Slot]:
    async with async_session() as session:
        query = select(Slot).where(Slot.id == slot_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
