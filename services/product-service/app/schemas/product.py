from typing import Optional, Any

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float = Field(gt=0)
    image_url: Optional[str] = None
    category: Optional[str] = "электроника"
    tags: list[str] = []
    attributes: dict[str, Any] = {}
    images: list[str] = []


class ProductAttrsUpdate(BaseModel):
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    attributes: Optional[dict[str, Any]] = None
    images: Optional[list[str]] = None


class ExtendedAttrs(BaseModel):
    category: Optional[str] = None
    tags: list[str] = []
    images: list[str] = []
    attributes: dict[str, Any] = {}
    rating: float = 0.0
    review_count: int = 0


class ProductOut(BaseModel):
    id: int
    name: str
    description: str
    price: float
    image_url: Optional[str]


class ProductExtended(ProductOut):
    extended_attrs: Optional[ExtendedAttrs] = None


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    skip: int
    limit: int


class ProductExtendedListOut(BaseModel):
    items: list[ProductExtended]
