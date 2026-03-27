import sys
import unittest
from pathlib import Path

_SERVICE_PATH = str(Path(__file__).parent.parent / "services" / "product-service")


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

import app.storage as storage
from app.config import settings
from app.main import app
from fastapi.testclient import TestClient
from jose import jwt as _jwt


def _make_token(user_id: int = 1, login: str = "admin") -> str:
    payload = {"sub": str(user_id), "login": login}
    return _jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


class TestProductService(unittest.TestCase):
    def setUp(self):
        storage._products.clear()
        storage._counter = 0
        self.client = TestClient(app, raise_server_exceptions=False)
        self.token = _make_token()

    def _create_product(self, name="iPhone 15", price=79990.0):
        return self.client.post(
            "/products",
            json={"name": name, "description": "desc", "price": price},
            headers={"Authorization": f"Bearer {self.token}"},
        )

    def test_create_product_returns_201(self):
        response = self._create_product()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertEqual(body["name"], "iPhone 15")
        self.assertEqual(body["price"], 79990.0)
        self.assertIn("id", body)

    def test_create_product_no_token_returns_401(self):
        response = self.client.post(
            "/products",
            json={"name": "Test", "description": "desc", "price": 100.0},
        )
        self.assertEqual(response.status_code, 401)

    def test_create_product_missing_price_returns_422(self):
        response = self.client.post(
            "/products",
            json={"name": "Test", "description": "desc"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.assertEqual(response.status_code, 422)

    def test_list_products_returns_200(self):
        self._create_product("Product A", 100.0)
        self._create_product("Product B", 200.0)
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total"], 2)
        self.assertEqual(len(body["items"]), 2)

    def test_list_products_pagination(self):
        for i in range(5):
            self._create_product(f"Product {i}", float(i * 100))
        response = self.client.get("/products", params={"skip": 2, "limit": 2})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["total"], 5)
        self.assertEqual(len(body["items"]), 2)
        self.assertEqual(body["skip"], 2)
        self.assertEqual(body["limit"], 2)

    def test_list_products_empty(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total"], 0)

    def test_get_product_by_id_returns_200(self):
        created = self._create_product().json()
        response = self.client.get(f"/products/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], created["id"])

    def test_get_product_unknown_id_returns_404(self):
        response = self.client.get("/products/99999")
        self.assertEqual(response.status_code, 404)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
