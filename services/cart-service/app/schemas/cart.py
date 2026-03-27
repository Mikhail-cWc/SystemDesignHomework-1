from typing import List, Optional

from pydantic import BaseModel


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product_name: Optional[str] = None
    price: Optional[float] = None


class CartOut(BaseModel):
    user_id: int
    items: List[CartItemOut]
    total_price: float
