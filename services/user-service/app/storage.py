from typing import Optional

_users: dict[int, dict] = {}
_login_index: dict[str, int] = {}
_counter: int = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def save(user_dict: dict) -> dict:
    _users[user_dict["id"]] = user_dict
    _login_index[user_dict["login"]] = user_dict["id"]
    return user_dict


def find_by_id(id: int) -> Optional[dict]:
    return _users.get(id)


def find_by_login(login: str) -> Optional[dict]:
    uid = _login_index.get(login)
    if uid is None:
        return None
    return _users.get(uid)


def search_by_name(q: str) -> list:
    q_lower = q.lower()
    result = []
    for user in _users.values():
        if q_lower in user["first_name"].lower() or q_lower in user["last_name"].lower():
            result.append(user)
    return result


def login_exists(login: str) -> bool:
    return login in _login_index
