import json

import aio_pika


class NotificationService:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url

    async def send_notification(self, user_id: int, text: str):
        connection = await aio_pika.connect_robust(self.amqp_url)
        channel = await connection.channel()
        queue = await channel.declare_queue("bot_notifications", durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({"user_id": user_id, "text": text}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )
        await connection.close()


_notification_service: NotificationService | None = None


def init_notification_service(amqp_url: str):
    global _notification_service
    _notification_service = NotificationService(amqp_url)


def get_notification_service() -> NotificationService:
    global _notification_service
    if _notification_service is None:
        raise RuntimeError("Notification service not initialized")
    return _notification_service
