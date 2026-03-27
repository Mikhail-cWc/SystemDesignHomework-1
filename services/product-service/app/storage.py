from typing import Optional

_products: dict[int, dict] = {}
_counter: int = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def save(product_dict: dict) -> dict:
    _products[product_dict["id"]] = product_dict
    return product_dict


def find_by_id(id: int) -> Optional[dict]:
    return _products.get(id)


def list_all(skip: int, limit: int) -> tuple:
    all_items = list(_products.values())
    total = len(all_items)
    return all_items[skip: skip + limit], total
