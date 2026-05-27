import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Update as TGUpdate
from fastapi import FastAPI
from redis.asyncio import Redis

from book_bot.bot.handlers import router as base_router
from book_bot.core.settings import BotSettings, settings  # type: ignore
from book_bot.services.notification import send_notification
from book_bot.tkq import broker

settings: BotSettings

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot
    global dp

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

        await send_notification(settings.ADMIN_TG, "БОТ ЗАПУЩЕН")
        yield

        print("Stopping application...")
        await dp.stop_polling()

        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            print("Pulling successful stopped")

    else:
        print(f"Starting in production-mode (Webhook): {settings.WEBHOOK_URL}")
        await bot.set_webhook(url=settings.WEBHOOK_URL, drop_pending_updates=True)

        yield

        await bot.delete_webhook()
        print("Stopping application")

    await redis_client.close()
    await bot.session.close()
    await broker.shutdown()


app = FastAPI(title="Telegram Bot Gateway", lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(update: dict[str, Any]):
    if not bot:
        raise Exception("Bot is not initialized")
    if not dp:
        raise Exception("Dp is not initialized")
    if settings.DEBUG:
        return {"status": "ok"}

    tg_update = TGUpdate(**update)
    await dp.feed_update(bot, tg_update)
    return {"status": "ok"}
