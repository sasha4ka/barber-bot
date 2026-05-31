from api.database import db


async def async_session():
    async with db.session_scope() as session:
        yield session
