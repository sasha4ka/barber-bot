from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from taskiq import TaskiqDepends
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from book_bot.core.settings import WorkerSettings, settings

settings: WorkerSettings

broker = RedisStreamBroker(url=settings.REDIS_URL).with_result_backend(
    result_backend=RedisAsyncResultBackend(settings.REDIS_URL)
)


async def get_bot():
    session = AiohttpSession(proxy=settings.PROXY_URL)

    async with Bot(token=settings.BOT_TOKEN, session=session) as bot_instance:
        yield bot_instance


@broker.task
async def send_message(
    user_id: int, text: str, bot: Bot = TaskiqDepends(get_bot)
) -> None:
    if not bot:
        print("Bot instance is not initialized")
        return
    print(f"HANDLING MESSAGE SEND: {user_id}, {text}")
    try:
        await bot.send_message(user_id, text, parse_mode=ParseMode.HTML)
    except Exception as er:
        print(f"Error while sending message: {er}")
