import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.redis import RedisStorage
from fastapi import FastAPI
from redis.asyncio import Redis

from book_bot.bot.handlers import router as base_router
from book_bot.core.settings import settings
from book_bot.tkq import broker

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot
    global dp

    storage: Optional[BaseStorage] = None

    redis_client = Redis.from_url(url=settings.REDIS_URL)
    storage = RedisStorage(redis=redis_client)
    print(f"Using redis storage. URL: {settings.REDIS_URL}")

    await broker.startup()

    if settings.PROXY_URL:
        session = AiohttpSession(proxy=settings.PROXY_URL)
        bot = Bot(token=settings.BOT_TOKEN, storage=storage, session=session)
        print(f"Using proxy: {settings.PROXY_URL}")
    else:
        bot = Bot(token=settings.BOT_TOKEN, storage=storage)

    dp = Dispatcher(storage=storage)
    dp.include_router(base_router)

    if settings.DEBUG:
        print("Starting in long-pulling mode...")
        await bot.delete_webhook(drop_pending_updates=True)
        polling_task = asyncio.create_task(dp.start_polling(bot))

        yield

        print("Stopping application...")
        await dp.stop_polling()

        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            print("Pulling successful stopped")

    else:
        print("Starting in production-mode (Webhook)...")
        await bot.set_webhook(url=settings.WEBHOOK_URL, drop_pending_updates=True)

        yield
        print("Stopping application")

    await redis_client.close()
    await bot.session.close()
    await broker.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(update: dict[str, Any]):
    if not bot:
        raise Exception("Bot is not initialized")
    if not dp:
        raise Exception("Dp is not initialized")
    if not settings.DEBUG:
        from aiogram.types import Update as TG_Update

        tg_update = TG_Update(**update)
        await dp.feed_update(bot, tg_update)
    return {"status": "ok"}
