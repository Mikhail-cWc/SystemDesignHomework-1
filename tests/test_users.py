import sys
import unittest
from pathlib import Path

_SERVICE_PATH = str(Path(__file__).parent.parent / "services" / "user-service")


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
from app.main import app
from fastapi.testclient import TestClient


class TestUserService(unittest.TestCase):
    def setUp(self):
        storage._users.clear()
        storage._login_index.clear()
        storage._counter = 0
        self.client = TestClient(app, raise_server_exceptions=False)

    def _register(self, login="Mikhail", password="password"):
        return self.client.post("/auth/register", json={
            "login": login,
            "first_name": "John",
            "last_name": "Doe",
            "password": password,
        })

    def test_register_returns_201_with_token(self):
        response = self._register()
        self.assertEqual(response.status_code, 201)
        body = response.json()
        self.assertIn("access_token", body)
        self.assertEqual(body["login"], "Mikhail")
        self.assertEqual(body["token_type"], "bearer")

    def test_register_duplicate_login_returns_409(self):
        self._register()
        response = self._register()
        self.assertEqual(response.status_code, 409)

    def test_register_missing_fields_returns_422(self):
        response = self.client.post("/auth/register", json={"login": "x"})
        self.assertEqual(response.status_code, 422)

    def test_login_returns_200_with_token(self):
        self._register()
        response = self.client.post("/auth/login", json={
            "login": "Mikhail",
            "password": "password",
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_login_wrong_password_returns_401(self):
        self._register()
        response = self.client.post("/auth/login", json={
            "login": "Mikhail",
            "password": "wrong",
        })
        self.assertEqual(response.status_code, 401)

    def test_login_unknown_user_returns_401(self):
        response = self.client.post("/auth/login", json={
            "login": "nobody",
            "password": "pass",
        })
        self.assertEqual(response.status_code, 401)

    def _get_token(self, login="Mikhail"):
        return self._register(login).json()["access_token"]

    def test_get_by_login_returns_user(self):
        token = self._get_token()
        response = self.client.get(
            "/users/by-login",
            params={"login": "Mikhail"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["login"], "Mikhail")

    def test_get_by_login_unknown_returns_404(self):
        token = self._get_token()
        response = self.client.get(
            "/users/by-login",
            params={"login": "nobody"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 404)

    def test_get_by_login_no_token_returns_401(self):
        response = self.client.get("/users/by-login", params={"login": "Mikhail"})
        self.assertEqual(response.status_code, 401)

    def test_search_returns_matching_users(self):
        token = self._get_token()
        self._register(login="janedoe")
        response = self.client.get(
            "/users/search",
            params={"q": "Doe"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_search_no_matches_returns_empty_list(self):
        token = self._get_token()
        response = self.client.get(
            "/users/search",
            params={"q": "zzznomatch"},
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_search_no_token_returns_401(self):
        response = self.client.get("/users/search", params={"q": "Jo"})
        self.assertEqual(response.status_code, 401)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
