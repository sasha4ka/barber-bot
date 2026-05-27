from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError

from book_bot.core.database import async_session
from book_bot.models.models import Master


async def get_masters() -> list[Master]:
    async with async_session() as session:
        result = await session.execute(select(Master))
        return list(result.scalars())


async def get_master(*, master_id: int) -> Optional[Master]:
    async with async_session() as session:
        query = select(Master).where(Master.id == master_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def create_master(
    *, full_name: str, tg_id: Optional[int] = None
) -> Optional[Master]:
    async with async_session() as session:
        master = Master(tg_id=tg_id, full_name=full_name)
        session.add(master)

        try:
            await session.commit()
            await session.refresh(master)
            return master
        except OperationalError, IntegrityError:
            await session.rollback()
            return None
