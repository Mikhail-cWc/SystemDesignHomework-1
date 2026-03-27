from typing import Optional

from app.schemas.user import UserCreate
from app.services.auth_service import hash_password, verify_password
from app import storage


def create_user(data: UserCreate) -> dict:
    uid = storage.next_id()
    user_dict = {
        "id": uid,
        "login": data.login,
        "first_name": data.first_name,
        "last_name": data.last_name,
        "hashed_password": hash_password(data.password),
    }
    return storage.save(user_dict)


def get_by_login(login: str) -> Optional[dict]:
    return storage.find_by_login(login)


def search_by_name(q: str) -> list:
    return storage.search_by_name(q)


def authenticate(login: str, password: str) -> Optional[dict]:
    user = storage.find_by_login(login)
    if user is None:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user
