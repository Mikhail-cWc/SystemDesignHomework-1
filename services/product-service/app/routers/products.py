from typing import Optional

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.db import get_pool, get_mongo_db
from app.schemas.product import (
    ProductAttrsUpdate,
    ProductCreate,
    ProductExtended,
    ProductExtendedListOut,
    ProductListOut,
    ProductOut,
)
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


@router.post("", status_code=201, response_model=ProductExtended)
async def create_product(
    data: ProductCreate,
    current_user: dict = Depends(get_current_user),
):
    pool: asyncpg.Pool = get_pool()
    mongo_db: AsyncIOMotorDatabase = get_mongo_db()
    return await product_service.create(pool, mongo_db, data)


@router.get("", status_code=200, response_model=ProductListOut | ProductExtendedListOut)
async def list_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1),
    tags: Optional[str] = Query(default=None, description="Теги через запятую: смартфон,apple. При использовании skip/limit игнорируются — возвращается до 100 результатов"),
):
    pool: asyncpg.Pool = get_pool()
    mongo_db: AsyncIOMotorDatabase = get_mongo_db()

    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        items = await product_service.list_by_tags(pool, mongo_db, tag_list)
        return ProductExtendedListOut(items=items)

    items, total = await product_service.list_products(pool, skip, limit)
    return ProductListOut(items=items, total=total, skip=skip, limit=limit)


@router.get("/{id}", status_code=200, response_model=ProductExtended)
async def get_product(
    id: int,
    extended: bool = Query(default=False, description="Включить расширенные атрибуты из MongoDB"),
):
    pool: asyncpg.Pool = get_pool()
    mongo_db: AsyncIOMotorDatabase = get_mongo_db()
    product = await product_service.get_by_id(pool, mongo_db, id, extended)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if extended:
        return ProductExtended(**product)
    return ProductOut(**product)


@router.put("/{id}/attrs", status_code=200)
async def update_product_attrs(
    id: int,
    data: ProductAttrsUpdate,
    current_user: dict = Depends(get_current_user),
):
    mongo_db: AsyncIOMotorDatabase = get_mongo_db()
    found = await product_service.update_attrs(mongo_db, id, data)
    if not found:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "updated"}


@router.delete("/{id}", status_code=204)
async def delete_product(
    id: int,
    current_user: dict = Depends(get_current_user),
):
    pool: asyncpg.Pool = get_pool()
    mongo_db: AsyncIOMotorDatabase = get_mongo_db()
    deleted = await product_service.delete(pool, mongo_db, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
