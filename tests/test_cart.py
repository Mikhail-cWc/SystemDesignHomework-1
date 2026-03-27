import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

_SERVICE_PATH = str(Path(__file__).parent.parent / "services" / "cart-service")


def _load_service():
    for key in list(sys.modules.keys()):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    if _SERVICE_PATH not in sys.path:
        sys.path.insert(0, _SERVICE_PATH)
    elif sys.path[0] != _SERVICE_PATH:
        sys.path.remove(_SERVICE_PATH)
        sys.path.insert(0, _SERVICE_PATH)


_load_service()

import app.http_client as http_client_module
import app.services.cart_service as cart_service_module
import app.storage as storage
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient
from jose import jwt as _jwt

MOCK_PRODUCT = {
    "id": 1,
    "name": "iPhone 15",
    "description": "Apple",
    "price": 79990.0,
    "image_url": None,
}


def _make_token(user_id: int = 1, login: str = "testuser") -> str:
    payload = {"sub": str(user_id), "login": login}
    return _jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


class TestCartService(unittest.TestCase):
    def setUp(self):
        storage._cart_items.clear()
        storage._counter = 0
        self.client = TestClient(app, raise_server_exceptions=False)
        self.token = _make_token(user_id=1)

    def _add_item(self, product_id: int = 1, quantity: int = 2):
        return self.client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": quantity},
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @patch.object(cart_service_module, "get_product", new_callable=AsyncMock, return_value=MOCK_PRODUCT)
    def test_add_item_returns_201(self, _mock):
        response = self._add_item()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["product_id"], 1)
        self.assertEqual(body["quantity"], 2)
        self.assertEqual(body["user_id"], 1)

    @patch.object(cart_service_module, "get_product", new_callable=AsyncMock, return_value=None)
    def test_add_item_unknown_product_returns_404(self, _mock):
        response = self._add_item(product_id=99999)
        self.assertEqual(response.status_code, 404)

    def test_add_item_no_token_returns_401(self):
        response = self.client.post("/cart/items", json={"product_id": 1, "quantity": 1})
        self.assertEqual(response.status_code, 401)

    @patch.object(cart_service_module, "get_product", new_callable=AsyncMock, return_value=MOCK_PRODUCT)
    def test_add_item_accumulates_quantity(self, _mock):
        self._add_item(quantity=2)
        self._add_item(quantity=3)
        response = self.client.get("/cart", headers={"Authorization": f"Bearer {self.token}"})
        items = response.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["quantity"], 5)

    @patch.object(cart_service_module, "get_product", new_callable=AsyncMock, return_value=MOCK_PRODUCT)
    def test_get_cart_returns_200(self, _mock):
        self._add_item()
        response = self.client.get("/cart", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["user_id"], 1)
        self.assertEqual(len(body["items"]), 1)
        self.assertAlmostEqual(body["total_price"], 79990.0 * 2)

    @patch.object(cart_service_module, "get_product", new_callable=AsyncMock, return_value=MOCK_PRODUCT)
    def test_get_cart_empty(self, _mock):
        response = self.client.get("/cart", headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["items"], [])
        self.assertEqual(body["total_price"], 0.0)

    def test_get_cart_no_token_returns_401(self):
        response = self.client.get("/cart")
        self.assertEqual(response.status_code, 401)

    @patch.object(cart_service_module, "get_product", new_callable=AsyncMock, return_value=MOCK_PRODUCT)
    def test_different_users_have_separate_carts(self, _mock):
        token_user2 = _make_token(user_id=2, login="user2")
        self._add_item(quantity=1)
        response = self.client.get("/cart", headers={"Authorization": f"Bearer {token_user2}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
