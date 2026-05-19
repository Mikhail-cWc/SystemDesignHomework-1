from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.db import init_pool, close_pool
from app.events import init_event_publisher, close_event_publisher
from app.routers import auth, users
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool(settings.db_url)
    await init_event_publisher(settings.rabbitmq_url)
    yield
    await close_event_publisher()
    await close_pool()


app = FastAPI(title="User Service", version="1.0.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


register_exception_handlers(app)
