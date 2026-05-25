from typing import Optional

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError, OperationalError

from book_bot.core.database import async_session
from book_bot.models.models import User


async def create_user(*, tg_id: int, full_name: str, phone_number: str) -> User | None:
    async with async_session() as session:
        user = User(tg_id=tg_id, full_name=full_name, phone=phone_number)
        session.add(user)

        try:
            await session.commit()
            await session.refresh(user)
            return user

        except OperationalError, IntegrityError:
            await session.rollback()
            return None


async def get_user(
    *, user_id: Optional[int] = None, tg_id: Optional[int] = None
) -> Optional[User]:
    if user_id:
        query = select(User).where(User.id == user_id)
    elif tg_id:
        query = select(User).where(User.tg_id == tg_id)
    else:
        return None

    async with async_session() as session:
        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_user_count() -> int:
    async with async_session() as session:
        query = select(func.count(User.id))
        result = await session.execute(query)
        return result.scalar_one()


async def modify_user(
    *, user: User, full_name: Optional[str] = None, phone_number: Optional[str] = None
) -> User:
    async with async_session() as session:
        session.add(user)

        if full_name:
            user.full_name = full_name
        if phone_number:
            user.phone = phone_number

        await session.commit()
        await session.refresh(user)
        return user


async def modify_user_by_id(
    *,
    user_id: Optional[int] = None,
    tg_id: Optional[int] = None,
    phone_number: Optional[str] = None,
    full_name: Optional[str] = None,
) -> Optional[User]:
    update_data = {}
    if phone_number:
        update_data["phone"] = phone_number
    if full_name:
        update_data["full_name"] = full_name
    if user_id:
        query = (
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )
    elif tg_id:
        query = (
            update(User)
            .where(User.tg_id == tg_id)
            .values(**update_data)
            .returning(User)
        )
    else:
        return

    async with async_session() as session:
        result = await session.execute(query)
        await session.commit()
        return result.scalar_one_or_none()


async def delete_user(
    *, user_id: Optional[int] = None, tg_id: Optional[int] = None
) -> bool:
    user = await get_user(user_id=user_id, tg_id=tg_id)

    if not user:
        return False

    async with async_session() as session:
        await session.delete(user)
        await session.commit()
        return True
