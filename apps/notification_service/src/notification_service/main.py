import asyncio
import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from notification_service.settings import settings

bot: Bot | None = None


async def process_message(message: AbstractIncomingMessage):
    global bot

    if bot is None:
        return

    async with message.process():
        data = json.loads(message.body.decode())
        user_id = data["user_id"]
        text = data["text"]

        try:
            await bot.send_message(
                chat_id=user_id, text=text, parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Failed to send message to user {user_id}: {e}")


async def main():
    global bot

    if settings.PROXY_URL:
        session = AiohttpSession(proxy=settings.PROXY_URL)
        bot = Bot(token=settings.BOT_TOKEN, session=session)
    else:
        bot = Bot(token=settings.BOT_TOKEN)

    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()

    await channel.set_qos(prefetch_count=10)

    queue = await channel.declare_queue("bot_notifications", durable=True)

    print("Notification service started...")
    await queue.consume(process_message)

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        print("Shutting down notification service...")
        await connection.close()
        await bot.session.close()


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
