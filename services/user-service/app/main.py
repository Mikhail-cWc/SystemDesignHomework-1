from fastapi import FastAPI

from app.routers import auth, users
from app.exceptions import register_exception_handlers

app = FastAPI(title="User Service", version="1.0.0")

app.include_router(auth.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


register_exception_handlers(app)
