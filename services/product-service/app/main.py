from fastapi import FastAPI

from app.exceptions import register_exception_handlers
from app.routers.products import router as products_router

app = FastAPI(title="Product Service", version="1.0.0", redirect_slashes=False)

app.include_router(products_router)

register_exception_handlers(app)


@app.get("/health")
def health():
    return {"status": "ok"}
