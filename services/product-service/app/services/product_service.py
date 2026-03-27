from typing import Optional

from app import storage
from app.schemas.product import ProductCreate


def create(data: ProductCreate) -> dict:
    product_dict = {
        "id": storage.next_id(),
        "name": data.name,
        "description": data.description,
        "price": data.price,
        "image_url": data.image_url,
    }
    return storage.save(product_dict)


def get_by_id(id: int) -> Optional[dict]:
    return storage.find_by_id(id)


def list_products(skip: int, limit: int) -> tuple:
    return storage.list_all(skip, limit)
