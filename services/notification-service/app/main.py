import asyncio
import json
import logging

import aio_pika

from app.config import settings

EXCHANGE_NAME = "shop.events"
QUEUE_NAME = "notifications.queue"
ROUTING_KEYS = ("user.registered", "product.created")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def handle_message(message: aio_pika.IncomingMessage) -> None:
    try:
        event = json.loads(message.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.exception("Invalid JSON event body")
        await message.ack()
        return

    try:
        logger.info(
            "Received event %s payload=%s",
            event.get("event_type"),
            event.get("payload"),
        )
        await message.ack()
    except Exception:
        logger.exception("Failed to process event")
        await message.nack(requeue=True)


async def main() -> None:
    connection = await aio_pika.connect_robust(settings.rabbitmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        for routing_key in ROUTING_KEYS:
            await queue.bind(exchange, routing_key=routing_key)

        logger.info("Notification service is consuming %s", QUEUE_NAME)
        await queue.consume(handle_message, no_ack=False)
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
