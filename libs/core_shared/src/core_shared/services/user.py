from typing import Optional

from core_shared.exc import UserNotFound
from core_shared.models import User
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_user(
    *, tg_id: int, full_name: str, phone_number: str, session: AsyncSession
) -> User | None:
    user = User(tg_id=tg_id, full_name=full_name, phone=phone_number)
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user


async def get_user(
    *, user_id: Optional[int] = None, tg_id: Optional[int] = None, session: AsyncSession
) -> Optional[User]:
    if user_id:
        query = select(User).where(User.id == user_id)
    elif tg_id:
        query = select(User).where(User.tg_id == tg_id)
    else:
        return None

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_user_count(session: AsyncSession) -> int:
    query = select(func.count(User.id))
    result = await session.execute(query)
    return result.scalar_one()


async def modify_user(
    *,
    user_id: Optional[int] = None,
    tg_id: Optional[int] = None,
    phone_number: Optional[str] = None,
    full_name: Optional[str] = None,
    session: AsyncSession,
) -> Optional[User]:
    update_data = {}
    if phone_number:
        update_data["phone"] = phone_number
    if full_name:
        update_data["full_name"] = full_name

    query = update(User).values(**update_data).returning(User)

    if user_id:
        query = query.where(User.id == user_id)
    elif tg_id:
        query = query.where(User.tg_id == tg_id)
    else:
        return

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def delete_user(
    *, user_id: Optional[int] = None, tg_id: Optional[int] = None, session: AsyncSession
):
    user = await get_user(user_id=user_id, tg_id=tg_id, session=session)

    if not user:
        raise UserNotFound

    await session.delete(user)
