import json
from datetime import datetime
from decimal import Decimal
from typing import Optional

import asyncpg
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.product import ProductCreate, ProductAttrsUpdate
from app import repository
from app.redis_client import get_redis

CACHE_TTL_LIST = 60
CACHE_TTL_ITEM = 120


def _serialize(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(type(obj))


async def _invalidate_lists() -> None:
    r = get_redis()
    if not r:
        return
    keys = []
    async for key in r.scan_iter("products:list:*"):
        keys.append(key)
    async for key in r.scan_iter("products:tags:*"):
        keys.append(key)
    if keys:
        await r.delete(*keys)


async def _invalidate_item(product_id: int) -> None:
    r = get_redis()
    if not r:
        return
    keys = []
    async for key in r.scan_iter(f"products:{product_id}*"):
        keys.append(key)
    if keys:
        await r.delete(*keys)


async def create(pool: asyncpg.Pool, mongo_db: AsyncIOMotorDatabase, data: ProductCreate) -> dict:
    result = await repository.create_product(
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
    await _invalidate_lists()
    return result


async def get_by_id(
    pool: asyncpg.Pool,
    mongo_db: Optional[AsyncIOMotorDatabase],
    product_id: int,
    extended: bool = False,
) -> Optional[dict]:
    r = get_redis()
    cache_key = f"products:{product_id}:extended" if extended else f"products:{product_id}"

    if r:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

    result = await repository.find_by_id(pool, mongo_db, product_id, extended)

    if result and r:
        await r.set(cache_key, json.dumps(result, default=_serialize), ex=CACHE_TTL_ITEM)

    return result


async def list_products(pool: asyncpg.Pool, skip: int, limit: int) -> tuple[list[dict], int]:
    r = get_redis()
    cache_key = f"products:list:{skip}:{limit}"

    if r:
        cached = await r.get(cache_key)
        if cached:
            data = json.loads(cached)
            return data["items"], data["total"]

    items, total = await repository.list_products(pool, skip, limit)

    if r:
        await r.set(
            cache_key,
            json.dumps({"items": items, "total": total}, default=_serialize),
            ex=CACHE_TTL_LIST,
        )

    return items, total


async def list_by_tags(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    tags: list[str],
) -> list[dict]:
    r = get_redis()
    sorted_tags = ",".join(sorted(tags))
    cache_key = f"products:tags:{sorted_tags}"

    if r:
        cached = await r.get(cache_key)
        if cached:
            return json.loads(cached)

    result = await repository.list_products_by_tags(pool, mongo_db, tags)

    if r:
        await r.set(cache_key, json.dumps(result, default=_serialize), ex=CACHE_TTL_LIST)

    return result


async def update_attrs(
    mongo_db: AsyncIOMotorDatabase,
    product_id: int,
    data: ProductAttrsUpdate,
) -> bool:
    result = await repository.update_product_attrs(
        mongo_db,
        product_id,
        data.model_dump(exclude_none=True),
    )
    if result:
        await _invalidate_item(product_id)
        await _invalidate_lists()
    return result


async def delete(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    product_id: int,
) -> bool:
    result = await repository.delete_product(pool, mongo_db, product_id)
    if result:
        await _invalidate_item(product_id)
        await _invalidate_lists()
    return result
