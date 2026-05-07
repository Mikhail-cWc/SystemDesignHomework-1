import time

from fastapi import HTTPException
from starlette.responses import JSONResponse

from app.redis_client import get_redis

RATE_LIMIT = 30
WINDOW_SECONDS = 60


async def check_rate_limit(user_id: int) -> dict:
    r = get_redis()
    if not r:
        return {"limit": RATE_LIMIT, "remaining": RATE_LIMIT, "reset": 0}

    now = int(time.time())
    window = now // WINDOW_SECONDS
    key = f"ratelimit:cart:{user_id}:{window}"

    current = await r.incr(key)
    if current == 1:
        await r.expire(key, WINDOW_SECONDS)

    remaining = max(0, RATE_LIMIT - current)
    reset = (window + 1) * WINDOW_SECONDS

    if current > RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail="Too Many Requests",
            headers={
                "X-RateLimit-Limit": str(RATE_LIMIT),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset),
                "Retry-After": str(reset - now),
            },
        )

    return {"limit": RATE_LIMIT, "remaining": remaining, "reset": reset}
