from typing import Tuple, List

import asyncpg
from fastapi import HTTPException

from app import repository


async def add_item(pool: asyncpg.Pool, user_id: int, product_id: int, quantity: int) -> dict:
    if not await repository.product_exists(pool, product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return await repository.add_item(pool, user_id, product_id, quantity)


async def get_cart(pool: asyncpg.Pool, user_id: int) -> Tuple[List[dict], float]:
    items = await repository.get_cart(pool, user_id)
    total_price = sum(float(item["price"]) * item["quantity"] for item in items)
    return items, total_price
