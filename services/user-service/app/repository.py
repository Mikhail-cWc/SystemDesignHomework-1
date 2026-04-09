from typing import Optional

import asyncpg


async def create_user(pool: asyncpg.Pool, login: str, first_name: str, last_name: str, password_hash: str) -> dict:
    row = await pool.fetchrow(
        """
        INSERT INTO users (login, first_name, last_name, password_hash)
        VALUES ($1, $2, $3, $4)
        RETURNING id, login, first_name, last_name, password_hash
        """,
        login, first_name, last_name, password_hash,
    )
    return dict(row)


async def find_by_login(pool: asyncpg.Pool, login: str) -> Optional[dict]:
    row = await pool.fetchrow(
        "SELECT id, login, first_name, last_name, password_hash FROM users WHERE login = $1",
        login,
    )
    return dict(row) if row else None


async def search_by_name(pool: asyncpg.Pool, q: str) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT id, login, first_name, last_name
        FROM users
        WHERE first_name ILIKE $1 OR last_name ILIKE $1
        """,
        f"%{q}%",
    )
    return [dict(r) for r in rows]


async def login_exists(pool: asyncpg.Pool, login: str) -> bool:
    row = await pool.fetchrow("SELECT 1 FROM users WHERE login = $1", login)
    return row is not None
