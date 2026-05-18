import datetime

from sqlalchemy import select

from book_bot.core.database import async_session
from book_bot.models import Slot


async def generate_slots_for_date(
    target_date: datetime.date,
    work_start: datetime.time,
    work_end: datetime.time,
    slot_duration_minutes: int = 60,
) -> list[Slot]:
    async with async_session() as session:
        existing_slots_query = select(Slot).where(Slot.date == target_date)
        existing_slots_result = await session.execute(existing_slots_query)
        if existing_slots_result.scalars().first():
            return []

        current_datetime = datetime.datetime.combine(target_date, work_start)
        end_datetime = datetime.datetime.combine(target_date, work_end)

        step = datetime.timedelta(minutes=slot_duration_minutes)
        new_slots: list[Slot] = []

        while current_datetime + step <= end_datetime:
            slot = Slot(
                date=target_date, time_start=current_datetime.time(), is_booked=False
            )
            new_slots.append(slot)
            current_datetime += step

        if new_slots:
            session.add_all(new_slots)
            await session.commit()

        return new_slots
