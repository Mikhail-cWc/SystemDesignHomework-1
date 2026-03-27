from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from app.routers.cart import router as cart_router
from app.exceptions import register_exception_handlers
import app.http_client as http_client_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client_module._client = httpx.AsyncClient()
    yield
    if http_client_module._client is not None:
        await http_client_module._client.aclose()
        http_client_module._client = None


app = FastAPI(title="Cart Service", version="1.0.0", lifespan=lifespan, redirect_slashes=False)

app.include_router(cart_router)

register_exception_handlers(app)


@app.get("/health")
async def health():
    return {"status": "ok"}
