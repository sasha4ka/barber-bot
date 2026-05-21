from taskiq import AsyncTaskiqTask

from book_bot.tkq import send_message


async def send_notification(user_id: int, text: str) -> AsyncTaskiqTask[None]:
    return await send_message.kiq(user_id, text)
