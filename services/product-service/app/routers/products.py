import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings
from app.db import get_pool
from app.schemas.product import ProductCreate, ProductListOut, ProductOut
from app.services import product_service

router = APIRouter(prefix="/products", tags=["products"], redirect_slashes=False)

_bearer = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    if not credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        return {"user_id": payload.get("sub"), "login": payload.get("login")}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("", status_code=201, response_model=ProductOut)
async def create_product(
    data: ProductCreate,
    current_user: dict = Depends(get_current_user),
):
    pool: asyncpg.Pool = get_pool()
    return await product_service.create(pool, data)


@router.get("", status_code=200, response_model=ProductListOut)
async def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1),
):
    pool: asyncpg.Pool = get_pool()
    items, total = await product_service.list_products(pool, skip, limit)
    return ProductListOut(items=items, total=total, skip=skip, limit=limit)


@router.get("/{id}", status_code=200, response_model=ProductOut)
async def get_product(id: int):
    pool: asyncpg.Pool = get_pool()
    product = await product_service.get_by_id(pool, id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
