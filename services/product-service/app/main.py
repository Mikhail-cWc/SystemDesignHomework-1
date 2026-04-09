from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_pool, close_pool
from app.exceptions import register_exception_handlers
from app.routers.products import router as products_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool(settings.db_url)
    yield
    await close_pool()


app = FastAPI(title="Product Service", version="1.0.0", redirect_slashes=False, lifespan=lifespan)

app.include_router(products_router)

register_exception_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
