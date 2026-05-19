import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "shop.events"

_connection = None
_channel = None
_exchange = None


def serialize_event_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(type(value))


def build_event(event_type: str, producer: str, payload: dict) -> dict:
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "producer": producer,
        "version": 1,
        "payload": payload,
    }


async def init_event_publisher(rabbitmq_url: str) -> None:
    global _connection, _channel, _exchange
    try:
        import aio_pika
    except ImportError:
        logger.warning("aio-pika is not installed; event publishing is disabled")
        return

    try:
        _connection = await aio_pika.connect_robust(rabbitmq_url)
        _channel = await _connection.channel()
        _exchange = await _channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
    except Exception:
        logger.exception("Failed to initialize RabbitMQ publisher")
        _connection = None
        _channel = None
        _exchange = None


async def close_event_publisher() -> None:
    global _connection, _channel, _exchange
    if _connection:
        await _connection.close()
    _connection = None
    _channel = None
    _exchange = None


async def publish_event(event_type: str, routing_key: str, payload: dict) -> None:
    if _exchange is None:
        logger.warning("RabbitMQ publisher is not initialized; skipped %s", event_type)
        return

    import aio_pika

    event = build_event(event_type, "user-service", payload)
    body = json.dumps(event, default=serialize_event_value, ensure_ascii=False).encode("utf-8")
    await _exchange.publish(
        aio_pika.Message(
            body=body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=routing_key,
    )
