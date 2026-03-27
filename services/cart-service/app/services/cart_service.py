from typing import List, Tuple

from fastapi import HTTPException
from app import storage
from app.http_client import get_product


async def add_item(user_id: int, product_id: int, quantity: int) -> dict:
    product = await get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    item = storage.add_item(user_id, product_id, quantity)
    enriched = dict(item)
    enriched["product_name"] = product.get("name")
    enriched["price"] = product.get("price")
    return enriched


async def get_cart(user_id: int) -> Tuple[List[dict], float]:
    items = storage.get_cart(user_id)
    enriched = []
    total_price = 0.0

    for item in items:
        enriched_item = dict(item)
        product = await get_product(item["product_id"])
        if product is not None:
            enriched_item["product_name"] = product.get("name")
            enriched_item["price"] = product.get("price")
            if enriched_item["price"] is not None:
                total_price += enriched_item["price"] * item["quantity"]
        enriched.append(enriched_item)

    return enriched, total_price
