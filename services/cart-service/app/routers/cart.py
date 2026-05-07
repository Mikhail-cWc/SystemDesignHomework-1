import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from starlette.responses import JSONResponse

from app.config import settings
from app.db import get_pool
from app.rate_limit import check_rate_limit
from app.schemas.cart import CartItemCreate, CartItemOut, CartOut
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"], redirect_slashes=False)

_bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return {"user_id": int(payload["sub"]), "login": payload["login"]}
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/items", status_code=status.HTTP_201_CREATED, response_model=CartItemOut)
async def add_item(body: CartItemCreate, current_user: dict = Depends(get_current_user)):
    rl = await check_rate_limit(current_user["user_id"])

    pool: asyncpg.Pool = get_pool()
    item = await cart_service.add_item(pool, current_user["user_id"], body.product_id, body.quantity)
    response = JSONResponse(
        status_code=201,
        content=CartItemOut(**item).model_dump(),
    )
    response.headers["X-RateLimit-Limit"] = str(rl["limit"])
    response.headers["X-RateLimit-Remaining"] = str(rl["remaining"])
    response.headers["X-RateLimit-Reset"] = str(rl["reset"])
    return response


@router.get("", status_code=status.HTTP_200_OK, response_model=CartOut)
async def get_cart(current_user: dict = Depends(get_current_user)):
    pool: asyncpg.Pool = get_pool()
    user_id = current_user["user_id"]
    items, total_price = await cart_service.get_cart(pool, user_id)
    return CartOut(user_id=user_id, items=[CartItemOut(**i) for i in items], total_price=total_price)
