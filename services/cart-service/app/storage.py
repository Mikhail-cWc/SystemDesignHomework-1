_cart_items: dict[int, list[dict]] = {}
_counter: int = 0


def next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def add_item(user_id: int, product_id: int, quantity: int) -> dict:
    if user_id not in _cart_items:
        _cart_items[user_id] = []

    for item in _cart_items[user_id]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            return item

    new_item = {
        "id": next_id(),
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
    }
    _cart_items[user_id].append(new_item)
    return new_item


def get_cart(user_id: int) -> list[dict]:
    return _cart_items.get(user_id, [])
