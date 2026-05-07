import json
from decimal import Decimal
from typing import Tuple, List

import asyncpg
from fastapi import HTTPException

from app import repository
from app.redis_client import get_redis

CACHE_TTL_CART = 30


def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(type(obj))


async def add_item(pool: asyncpg.Pool, user_id: int, product_id: int, quantity: int) -> dict:
    if not await repository.product_exists(pool, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    result = await repository.add_item(pool, user_id, product_id, quantity)

    r = get_redis()
    if r:
        await r.delete(f"cart:{user_id}")

    return result


async def get_cart(pool: asyncpg.Pool, user_id: int) -> Tuple[List[dict], float]:
    r = get_redis()
    cache_key = f"cart:{user_id}"

    if r:
        cached = await r.get(cache_key)
        if cached:
            data = json.loads(cached)
            return data["items"], data["total_price"]

    items = await repository.get_cart(pool, user_id)
    total_price = sum(float(item["price"]) * item["quantity"] for item in items)

    if r:
        await r.set(
            cache_key,
            json.dumps({"items": items, "total_price": total_price}, default=_serialize),
            ex=CACHE_TTL_CART,
        )

    return items, total_price
