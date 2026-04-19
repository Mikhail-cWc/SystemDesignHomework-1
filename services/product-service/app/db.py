import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_pool: asyncpg.Pool | None = None
_mongo_client: AsyncIOMotorClient | None = None
_mongo_db: AsyncIOMotorDatabase | None = None


async def init_pool(dsn: str) -> None:
    global _pool
    _pool = await asyncpg.create_pool(dsn)


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    return _pool


def init_mongo(url: str, db_name: str) -> None:
    global _mongo_client, _mongo_db
    _mongo_client = AsyncIOMotorClient(url)
    _mongo_db = _mongo_client[db_name]


async def close_mongo() -> None:
    global _mongo_client, _mongo_db
    if _mongo_client:
        _mongo_client.close()
        _mongo_client = None
        _mongo_db = None


def get_mongo_db() -> AsyncIOMotorDatabase:
    return _mongo_db
