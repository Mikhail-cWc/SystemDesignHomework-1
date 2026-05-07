from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_pool, close_pool
from app.redis_client import init_redis, close_redis
from app.routers.cart import router as cart_router
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool(settings.db_url)
    await init_redis(settings.redis_url)
    yield
    await close_redis()
    await close_pool()


app = FastAPI(title="Cart Service", version="1.0.0", lifespan=lifespan, redirect_slashes=False)

app.include_router(cart_router)

register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
