from typing import Optional

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: Optional[str]


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    skip: int
    limit: int
