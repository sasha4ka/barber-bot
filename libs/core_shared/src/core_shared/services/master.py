import asyncio
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from core_shared.exc import PasswordAuthenticationError
from core_shared.models import Master
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession


class MasterNotFoundError(Exception):
    pass


class AuthService:
    def __init__(self):
        self.ph = PasswordHasher()

    async def validate_password(self, hashed_password: str, password: str) -> bool:
        try:
            await asyncio.to_thread(self.ph.verify, hashed_password, password)
            return True
        except VerifyMismatchError:
            return False

    async def hash_password(self, password: str) -> str:
        return await asyncio.to_thread(self.ph.hash, password)


auth_service = AuthService()


async def get_masters(*, session: AsyncSession) -> list[Master]:
    result = await session.execute(select(Master))
    return list(result.scalars())


async def get_master(*, master_id: int, session: AsyncSession) -> Optional[Master]:
    query = select(Master).where(Master.id == master_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_master_by_username(
    *, username: str, session: AsyncSession
) -> Optional[Master]:
    query = select(Master).where(Master.username == username)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def increment_token_version(*, master_id: int, session: AsyncSession) -> int:
    query = (
        update(Master)
        .where(Master.id == master_id)
        .values(token_version=Master.token_version + 1)
        .returning(Master)
    )
    result = await session.execute(query)
    master = result.scalar_one_or_none()

    if master is None:
        raise MasterNotFoundError("Master not found")

    return master.token_version


async def create_master(
    *,
    username: str,
    password: str,
    full_name: str,
    tg_id: Optional[int] = None,
    session: AsyncSession,
) -> Master:
    password_hash = await auth_service.hash_password(password)
    master = Master(
        username=username, password_hash=password_hash, full_name=full_name, tg_id=tg_id
    )
    session.add(master)

    await session.flush()
    await session.refresh(master)

    return master


async def update_master_password(
    *,
    master_id: int,
    new_password: str,
    session: AsyncSession,
) -> None:
    master = await get_master(master_id=master_id, session=session)
    if master is None:
        raise MasterNotFoundError("Master not found")

    master.password_hash = await auth_service.hash_password(new_password)
    await session.flush()


async def validate_master(
    *, username: str, password: str, session: AsyncSession
) -> Master:
    master = await get_master_by_username(username=username, session=session)
    if master is None:
        raise PasswordAuthenticationError("Incorrect username or password")

    if not await auth_service.validate_password(master.password_hash, password):
        raise PasswordAuthenticationError("Incorrect username or password")

    return master
