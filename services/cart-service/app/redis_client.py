import redis.asyncio as redis

_redis: redis.Redis | None = None


async def init_redis(url: str) -> None:
    global _redis
    _redis = redis.from_url(url, decode_responses=True)


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


def get_redis() -> redis.Redis:
    return _redis
