from typing import Optional

import asyncpg


async def create_product(pool: asyncpg.Pool, name: str, description: Optional[str], price: float, image_url: Optional[str]) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO products (name, description, price, image_url)
        VALUES ($1, $2, $3, $4)
        RETURNING id, name, description, price, image_url
        """,
        name, description, price, image_url,
    )
    return dict(row)


async def find_by_id(pool: asyncpg.Pool, product_id: int) -> Optional[dict]:
    row = await pool.fetchrow(
        "SELECT id, name, description, price, image_url FROM products WHERE id = $1",
        product_id,
    )
    return dict(row) if row else None


async def list_products(pool: asyncpg.Pool, skip: int, limit: int) -> tuple[list[dict], int]:
    rows = await pool.fetch(
        "SELECT id, name, description, price, image_url FROM products ORDER BY id LIMIT $1 OFFSET $2",
        limit, skip,
    )
    total = await pool.fetchval("SELECT COUNT(*) FROM products")
    return [dict(r) for r in rows], total
