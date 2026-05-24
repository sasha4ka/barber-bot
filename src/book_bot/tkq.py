from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from book_bot.core.settings import settings

broker = RedisStreamBroker(url=settings.REDIS_URL).with_result_backend(
    result_backend=RedisAsyncResultBackend(settings.REDIS_URL)
)

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


@broker.task
async def send_message(user_id: int, text: str) -> None:
    if not bot:
        return
    try:
        await bot.send_message(user_id, text, parse_mode=ParseMode.HTML)
    except Exception as er:
        print(f"Error while sending message: {er}")


@broker.on_event("startup")
async def startup():
    global bot
    global dp
    session = AiohttpSession(proxy=settings.SOCKS5_PROXY)
    bot = Bot(token=settings.BOT_TOKEN, session=session)
    dp = Dispatcher()
    print("Notification server started")


@broker.on_event("shutdown")
async def shutdown():
    await bot.session.close()
    print("Notification server stopped")
