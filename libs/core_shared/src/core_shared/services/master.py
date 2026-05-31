from typing import Optional

from core_shared.models import Master
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_masters(*, session: AsyncSession) -> list[Master]:
    result = await session.execute(select(Master))
    return list(result.scalars())


async def get_master(*, master_id: int, session: AsyncSession) -> Optional[Master]:
    query = select(Master).where(Master.id == master_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def create_master(
    *, full_name: str, tg_id: Optional[int] = None, session: AsyncSession
) -> Optional[Master]:
    master = Master(tg_id=tg_id, full_name=full_name)
    session.add(master)

    await session.flush()
    await session.refresh(master)
    return master
