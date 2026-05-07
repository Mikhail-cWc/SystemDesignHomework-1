from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_pool, close_pool, init_mongo, close_mongo
from app.redis_client import init_redis, close_redis
from app.exceptions import register_exception_handlers
from app.routers.products import router as products_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool(settings.db_url)
    init_mongo(settings.mongo_url, settings.mongo_db_name)
    await init_redis(settings.redis_url)
    yield
    await close_redis()
    await close_pool()
    await close_mongo()


app = FastAPI(title="Product Service", version="1.0.0", redirect_slashes=False, lifespan=lifespan)

app.include_router(products_router)

register_exception_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
