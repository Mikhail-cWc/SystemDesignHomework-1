from datetime import datetime, timezone
from typing import Optional

import asyncpg
from motor.motor_asyncio import AsyncIOMotorDatabase


async def create_product(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    name: str,
    description: Optional[str],
    price: float,
    image_url: Optional[str],
    category: Optional[str],
    tags: list[str],
    attributes: dict,
    images: list[str],
) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO products (name, description, price, image_url)
        VALUES ($1, $2, $3, $4)
        RETURNING id, name, description, price, image_url
        """,
        name, description, price, image_url,
    )
    product = dict(row)
    product_id = str(product["id"])

    mongo_doc = {
        "product_id": product_id,
        "category": category or "электроника",
        "tags": tags,
        "images": images or ([image_url] if image_url else []),
        "attributes": attributes,
        "rating": 0.0,
        "review_count": 0,
        "created_at": datetime.now(timezone.utc),
    }
    await mongo_db["product_attrs"].insert_one(mongo_doc)

    product["extended_attrs"] = {
        "category": mongo_doc["category"],
        "tags": mongo_doc["tags"],
        "images": mongo_doc["images"],
        "attributes": mongo_doc["attributes"],
        "rating": mongo_doc["rating"],
        "review_count": mongo_doc["review_count"],
    }
    return product


async def find_by_id(
    pool: asyncpg.Pool,
    mongo_db: Optional[AsyncIOMotorDatabase],
    product_id: int,
    extended: bool = False,
) -> Optional[dict]:
    row = await pool.fetchrow(
        "SELECT id, name, description, price, image_url FROM products WHERE id = $1",
        product_id,
    )
    if not row:
        return None
    product = dict(row)

    if extended and mongo_db is not None:
        mongo_doc = await mongo_db["product_attrs"].find_one(
            {"product_id": str(product_id)},
            {"_id": 0, "product_id": 0},
        )
        product["extended_attrs"] = mongo_doc or {}

    return product


async def list_products(pool: asyncpg.Pool, skip: int, limit: int) -> tuple[list[dict], int]:
    rows = await pool.fetch(
        "SELECT id, name, description, price, image_url FROM products ORDER BY id LIMIT $1 OFFSET $2",
        limit, skip,
    )
    total = await pool.fetchval("SELECT COUNT(*) FROM products")
    return [dict(r) for r in rows], total


async def list_products_by_tags(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    tags: list[str],
) -> list[dict]:
    cursor = mongo_db["product_attrs"].find(
        {"tags": {"$in": tags}},
        {"_id": 0},
    )
    mongo_docs = await cursor.to_list(length=100)
    if not mongo_docs:
        return []

    ids = [int(d["product_id"]) for d in mongo_docs if d["product_id"].isdigit()]
    if not ids:
        return []

    rows = await pool.fetch(
        "SELECT id, name, description, price, image_url FROM products WHERE id = ANY($1::int[])",
        ids,
    )
    pg_map = {r["id"]: dict(r) for r in rows}
    mongo_map = {d["product_id"]: d for d in mongo_docs}

    result = []
    for product_id in ids:
        pg = pg_map.get(product_id)
        if not pg:
            continue
        mongo = mongo_map.get(str(product_id), {})
        pg["extended_attrs"] = {k: v for k, v in mongo.items() if k != "product_id"}
        result.append(pg)
    return result


async def update_product_attrs(
    mongo_db: AsyncIOMotorDatabase,
    product_id: int,
    update_data: dict,
) -> bool:
    set_fields = {}
    if "tags" in update_data:
        set_fields["tags"] = update_data["tags"]
    if "attributes" in update_data:
        set_fields["attributes"] = update_data["attributes"]
    if "images" in update_data:
        set_fields["images"] = update_data["images"]
    if "category" in update_data:
        set_fields["category"] = update_data["category"]

    if not set_fields:
        return True

    result = await mongo_db["product_attrs"].update_one(
        {"product_id": str(product_id)},
        {"$set": set_fields},
    )
    return result.matched_count > 0


async def delete_product(
    pool: asyncpg.Pool,
    mongo_db: AsyncIOMotorDatabase,
    product_id: int,
) -> bool:
    result = await pool.execute(
        "DELETE FROM products WHERE id = $1",
        product_id,
    )
    await mongo_db["product_attrs"].delete_one({"product_id": str(product_id)})
    return result != "DELETE 0"
