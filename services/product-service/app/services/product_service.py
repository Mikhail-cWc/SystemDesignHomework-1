from typing import Optional

import asyncpg
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.product import ProductCreate, ProductAttrsUpdate
from app import repository


async def create(pool: asyncpg.Pool, mongo_db: AsyncIOMotorDatabase, data: ProductCreate) -> dict:
    return await repository.create_product(
        pool,
        mongo_db,
        name=data.name,
        description=data.description,
        price=data.price,
        image_url=data.image_url,
        category=data.category,
        tags=data.tags,
        attributes=data.attributes,
        images=data.images,
    )


async def get_by_id(
    pool: asyncpg.Pool,
    mongo_db: Optional[AsyncIOMotorDatabase],
    product_id: int,
    extended: bool = False,
) -> Optional[dict]:
    return await repository.find_by_id(pool, mongo_db, product_id, extended)


async def list_products(pool: asyncpg.Pool, skip: int, limit: int) -> tuple[list[dict], int]:
    return await repository.list_products(pool, skip, limit)


async def list_by_tags(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    tags: list[str],
) -> list[dict]:
    return await repository.list_products_by_tags(pool, mongo_db, tags)


async def update_attrs(
    mongo_db: AsyncIOMotorDatabase,
    product_id: int,
    data: ProductAttrsUpdate,
) -> bool:
    return await repository.update_product_attrs(
        mongo_db,
        product_id,
        data.model_dump(exclude_none=True),
    )


async def delete(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    product_id: int,
) -> bool:
    return await repository.delete_product(pool, mongo_db, product_id)
