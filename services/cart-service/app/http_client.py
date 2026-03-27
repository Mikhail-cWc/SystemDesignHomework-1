from typing import Optional

import httpx
from app.config import settings

_client: Optional[httpx.AsyncClient] = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient()
    return _client


async def get_product(product_id: int) -> Optional[dict]:
    client = get_client()
    try:
        response = await client.get(f"{settings.product_service_url}/products/{product_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except Exception:
        return None
