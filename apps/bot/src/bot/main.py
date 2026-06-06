import asyncio
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from core_shared.services.notification import (
    get_notification_service,
    init_notification_service,
)
from redis.asyncio import Redis

from bot.core.settings import settings
from bot.handlers import router as base_router

bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


async def on_startup(bot: Bot):
    if settings.DEBUG:
        await bot.delete_webhook(drop_pending_updates=True)
        notification_service = get_notification_service()
        await notification_service.send_notification(settings.ADMIN_TG, "БОТ ЗАПУЩЕН")
    else:
        await bot.set_webhook(url=settings.WEBHOOK_URL, drop_pending_updates=True)


async def on_close(bot: Bot, redis_client: Redis):
    await bot.session.close()
    await redis_client.close()
    print("Bot shutdown complete")


async def main():
    redis_client = Redis.from_url(url=settings.REDIS_URL)  # type: ignore
    storage = RedisStorage(redis=redis_client)
    print("Using redis storage. URL: ", settings.REDIS_URL)

    dp = Dispatcher(storage=storage)
    dp.include_router(base_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_close)

    dp["redis_client"] = redis_client

    if settings.PROXY_URL:
        print("Using proxy. URL: ", settings.PROXY_URL)
        session = AiohttpSession(proxy=settings.PROXY_URL)
        bot = Bot(
            token=settings.BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(parse_mode="HTML"),
        )
    else:
        bot = Bot(
            token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML")
        )

    init_notification_service(settings.RABBITMQ_URL)

    if settings.DEBUG:
        print("Starting in long-pulling mode...")
        await dp.start_polling(bot)  # type: ignore

    else:
        print(f"Starting in production-mode (Webhook): {settings.WEBHOOK_URL}")

        app = web.Application()

        handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
        handler.register(app, path="/webhook")

        setup_application(app, dp, bot=bot)

        web.run_app(app, host="0.0.0.0", port=8000)


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
