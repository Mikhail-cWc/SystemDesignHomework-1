import importlib
import json
import sys
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).parent.parent


def load_service_module(service_name: str, module_name: str):
    service_path = str(ROOT / "services" / service_name)
    for key in list(sys.modules):
        if key == "app" or key.startswith("app."):
            del sys.modules[key]
    if service_path in sys.path:
        sys.path.remove(service_path)
    sys.path.insert(0, service_path)
    return importlib.import_module(module_name)


class TestEventEnvelope(unittest.TestCase):
    def test_user_registered_event_has_common_envelope_fields(self):
        events = load_service_module("user-service", "app.events")

        event = events.build_event(
            event_type="UserRegistered",
            producer="user-service",
            payload={
                "user_id": 1,
                "login": "Mikhail",
                "first_name": "Михаил",
                "last_name": "Копылов",
            },
        )

        self.assertEqual(event["event_type"], "UserRegistered")
        self.assertEqual(event["producer"], "user-service")
        self.assertEqual(event["version"], 1)
        self.assertIn("event_id", event)
        self.assertIn("occurred_at", event)
        self.assertEqual(event["payload"]["user_id"], 1)
        self.assertEqual(event["payload"]["login"], "Mikhail")
        self.assertEqual(event["payload"]["first_name"], "Михаил")
        self.assertEqual(event["payload"]["last_name"], "Копылов")

    def test_product_created_event_serializes_decimal_price(self):
        events = load_service_module("product-service", "app.events")

        event = events.build_event(
            event_type="ProductCreated",
            producer="product-service",
            payload={
                "product_id": 10,
                "name": "iPhone 15",
                "price": Decimal("79990.00"),
                "category": "электроника",
                "tags": ["смартфон", "apple", "ios"],
            },
        )

        serialized = json.loads(json.dumps(event, default=events.serialize_event_value))
        self.assertEqual(serialized["event_type"], "ProductCreated")
        self.assertEqual(serialized["producer"], "product-service")
        self.assertEqual(serialized["payload"]["product_id"], 10)
        self.assertEqual(serialized["payload"]["price"], 79990.0)
        self.assertEqual(serialized["payload"]["category"], "электроника")
        self.assertEqual(serialized["payload"]["tags"], ["смартфон", "apple", "ios"])


if __name__ == "__main__":
    unittest.main()
