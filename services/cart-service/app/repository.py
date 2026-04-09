import asyncpg


async def add_item(pool: asyncpg.Pool, user_id: int, product_id: int, quantity: int) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO cart_items (user_id, product_id, quantity)
        VALUES ($1, $2, $3)
        ON CONFLICT ON CONSTRAINT uq_cart_user_product
        DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity
        RETURNING id, user_id, product_id, quantity
        """,
        user_id, product_id, quantity,
    )
    return dict(row)


async def get_cart(pool: asyncpg.Pool, user_id: int) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT
            ci.id,
            ci.user_id,
            ci.product_id,
            ci.quantity,
            p.name  AS product_name,
            p.price AS price
        FROM cart_items ci
        JOIN products p ON p.id = ci.product_id
        WHERE ci.user_id = $1
        ORDER BY ci.added_at
        """,
        user_id,
    )
    return [dict(r) for r in rows]


async def product_exists(pool: asyncpg.Pool, product_id: int) -> bool:
    row = await pool.fetchrow("SELECT 1 FROM products WHERE id = $1", product_id)
    return row is not None
