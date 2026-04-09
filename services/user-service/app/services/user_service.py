from typing import Optional

import asyncpg

from app.schemas.user import UserCreate
from app.services.auth_service import hash_password, verify_password
from app import repository


async def create_user(pool: asyncpg.Pool, data: UserCreate) -> dict:
    return await repository.create_user(
        pool,
        login=data.login,
        first_name=data.first_name,
        last_name=data.last_name,
        password_hash=hash_password(data.password),
    )


async def get_by_login(pool: asyncpg.Pool, login: str) -> Optional[dict]:
    return await repository.find_by_login(pool, login)


async def search_by_name(pool: asyncpg.Pool, q: str) -> list[dict]:
    return await repository.search_by_name(pool, q)


async def authenticate(pool: asyncpg.Pool, login: str, password: str) -> Optional[dict]:
    user = await repository.find_by_login(pool, login)
    if user is None:
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user
