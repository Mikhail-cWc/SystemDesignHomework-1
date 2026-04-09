from typing import Optional

import asyncpg

from app.schemas.product import ProductCreate
from app import repository


async def create(pool: asyncpg.Pool, data: ProductCreate) -> dict:
    return await repository.create_product(
        pool,
        name=data.name,
        description=data.description,
        price=data.price,
        image_url=data.image_url,
    )


async def get_by_id(pool: asyncpg.Pool, product_id: int) -> Optional[dict]:
    return await repository.find_by_id(pool, product_id)


async def list_products(pool: asyncpg.Pool, skip: int, limit: int) -> tuple[list[dict], int]:
    return await repository.list_products(pool, skip, limit)
