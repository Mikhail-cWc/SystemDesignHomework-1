import os
import unittest

import httpx
from jose import jwt as _jwt

BASE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:8002")
JWT_SECRET = os.getenv("JWT_SECRET", "CHANGEME")
JWT_ALGORITHM = "HS256"


def _make_token(user_id: int = 1, login: str = "testrunner") -> str:
    return _jwt.encode(
        {"sub": str(user_id), "login": login},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


class TestProductService(unittest.TestCase):
    def setUp(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=10.0)
        self.token = _make_token()
        self.auth = {"Authorization": f"Bearer {self.token}"}
        self._created_ids: list[int] = []

    def tearDown(self):
        for pid in self._created_ids:
            self.client.delete(f"/products/{pid}", headers=self.auth)
        self.client.close()

    def _create_product(
        self,
        name: str = "Test Product",
        price: float = 999.0,
        tags: list[str] | None = None,
        category: str = "электроника",
    ) -> dict:
        payload: dict = {
            "name": name,
            "description": "test description",
            "price": price,
            "category": category,
        }
        if tags is not None:
            payload["tags"] = tags
        resp = self.client.post("/products", json=payload, headers=self.auth)
        self.assertEqual(resp.status_code, 201, resp.text)
        body = resp.json()
        self._created_ids.append(body["id"])
        return body

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "ok"})

    def test_create_product_returns_201(self):
        body = self._create_product(name="Создание продукта", price=12345.0)
        self.assertEqual(body["name"], "Создание продукта")
        self.assertEqual(body["price"], 12345.0)
        self.assertIn("id", body)

    def test_create_product_includes_extended_attrs(self):
        body = self._create_product(tags=["тест", "новый"])
        ext = body.get("extended_attrs", {})
        self.assertIn("тест", ext.get("tags", []))
        self.assertEqual(ext.get("rating"), 0.0)
        self.assertEqual(ext.get("review_count"), 0)

    def test_create_product_no_token_returns_401(self):
        resp = self.client.post(
            "/products",
            json={"name": "Hack", "description": "x", "price": 1.0},
        )
        self.assertEqual(resp.status_code, 401)

    def test_create_product_missing_price_returns_422(self):
        resp = self.client.post(
            "/products",
            json={"name": "NoPriceProduct", "description": "x"},
            headers=self.auth,
        )
        self.assertEqual(resp.status_code, 422)

    def test_create_product_negative_price_returns_422(self):
        resp = self.client.post(
            "/products",
            json={"name": "NegPrice", "description": "x", "price": -1.0},
            headers=self.auth,
        )
        self.assertEqual(resp.status_code, 422)

    def test_create_product_zero_price_returns_422(self):
        resp = self.client.post(
            "/products",
            json={"name": "ZeroPrice", "description": "x", "price": 0},
            headers=self.auth,
        )
        self.assertEqual(resp.status_code, 422)

    def test_get_product_returns_200(self):
        created = self._create_product()
        resp = self.client.get(f"/products/{created['id']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], created["id"])

    def test_get_product_extended_includes_mongo_attrs(self):
        created = self._create_product(tags=["mongo-тест"])
        resp = self.client.get(f"/products/{created['id']}", params={"extended": "true"})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("extended_attrs", body)
        self.assertIn("mongo-тест", body["extended_attrs"]["tags"])

    def test_get_product_unknown_id_returns_404(self):
        resp = self.client.get("/products/999999999")
        self.assertEqual(resp.status_code, 404)

    def test_list_products_returns_200(self):
        resp = self.client.get("/products")
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIn("items", body)
        self.assertIn("total", body)
        self.assertIn("skip", body)
        self.assertIn("limit", body)

    def test_list_products_pagination_limit(self):
        resp = self.client.get("/products", params={"skip": 0, "limit": 3})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertLessEqual(len(body["items"]), 3)
        self.assertEqual(body["limit"], 3)
        self.assertEqual(body["skip"], 0)

    def test_list_products_created_appear_in_list(self):
        total_before = self.client.get("/products", params={"limit": 1}).json()["total"]
        a = self._create_product(name="ListTestA")
        b = self._create_product(name="ListTestB")
        resp = self.client.get("/products", params={"skip": total_before, "limit": 10})
        body = resp.json()
        self.assertEqual(body["total"], total_before + 2)
        ids = [item["id"] for item in body["items"]]
        self.assertIn(a["id"], ids)
        self.assertIn(b["id"], ids)

    def test_list_by_tags_returns_matching_products(self):
        unique_tag = "уникальный-тег-12345"
        self._create_product(name="TagProduct", tags=[unique_tag])
        resp = self.client.get("/products", params={"tags": unique_tag})
        self.assertEqual(resp.status_code, 200)
        items = resp.json()["items"]
        self.assertTrue(any(unique_tag in i["extended_attrs"]["tags"] for i in items))

    def test_list_by_tags_no_match_returns_empty(self):
        resp = self.client.get("/products", params={"tags": "тег-которого-точно-нет-xyzabc"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["items"], [])

    def test_update_attrs_returns_200(self):
        created = self._create_product()
        resp = self.client.put(
            f"/products/{created['id']}/attrs",
            json={"tags": ["обновлено"], "category": "электроника"},
            headers=self.auth,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {"status": "updated"})

    def test_update_attrs_persisted_in_mongo(self):
        created = self._create_product(tags=["старый"])
        self.client.put(
            f"/products/{created['id']}/attrs",
            json={"tags": ["новый-тег"]},
            headers=self.auth,
        )
        resp = self.client.get(f"/products/{created['id']}", params={"extended": "true"})
        tags = resp.json()["extended_attrs"]["tags"]
        self.assertIn("новый-тег", tags)
        self.assertNotIn("старый", tags)

    def test_update_attrs_unknown_product_returns_404(self):
        resp = self.client.put(
            "/products/999999999/attrs",
            json={"tags": ["x"]},
            headers=self.auth,
        )
        self.assertEqual(resp.status_code, 404)

    def test_update_attrs_no_token_returns_401(self):
        created = self._create_product()
        resp = self.client.put(
            f"/products/{created['id']}/attrs",
            json={"tags": ["x"]},
        )
        self.assertEqual(resp.status_code, 401)

    def test_delete_returns_204(self):
        created = self._create_product()
        pid = created["id"]
        self._created_ids.remove(pid)
        resp = self.client.delete(f"/products/{pid}", headers=self.auth)
        self.assertEqual(resp.status_code, 204)

    def test_delete_product_not_found_in_pg_after_delete(self):
        created = self._create_product()
        pid = created["id"]
        self._created_ids.remove(pid)
        self.client.delete(f"/products/{pid}", headers=self.auth)
        resp = self.client.get(f"/products/{pid}")
        self.assertEqual(resp.status_code, 404)

    def test_delete_product_not_found_in_mongo_after_delete(self):
        unique_tag = "удаляемый-тег-99999"
        created = self._create_product(tags=[unique_tag])
        pid = created["id"]
        self._created_ids.remove(pid)
        self.client.delete(f"/products/{pid}", headers=self.auth)
        resp = self.client.get("/products", params={"tags": unique_tag})
        self.assertEqual(resp.json()["items"], [])

    def test_delete_unknown_product_returns_404(self):
        resp = self.client.delete("/products/999999999", headers=self.auth)
        self.assertEqual(resp.status_code, 404)

    def test_delete_no_token_returns_401(self):
        created = self._create_product()
        resp = self.client.delete(f"/products/{created['id']}")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
