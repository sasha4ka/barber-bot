import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from fastapi import FastAPI

from book_bot.bot.handlers import router
from book_bot.core.settings import settings

bot: Optional[Bot] = None
dp = Dispatcher()
dp.include_router(router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot

    if settings.DEBUG and getattr(settings, "SOCKS5_PROXY", None):
        session = AiohttpSession(proxy=settings.SOCKS5_PROXY)
        bot = Bot(token=settings.BOT_TOKEN, session=session)
    else:
        bot = Bot(token=settings.BOT_TOKEN)

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

    await bot.session.close()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(update: dict[str, Any]):
    if not bot:
        raise Exception("Bot is not initialized")
    if not settings.DEBUG:
        from aiogram.types import Update as TG_Update

        tg_update = TG_Update(**update)
        await dp.feed_update(bot, tg_update)
    return {"status": "ok"}
