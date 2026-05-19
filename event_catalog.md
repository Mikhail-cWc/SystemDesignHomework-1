# Event Catalog

## Общий формат

Все события публикуются в RabbitMQ exchange `shop.events` с типом `topic`.

```json
{
  "event_id": "uuid",
  "event_type": "EventName",
  "occurred_at": "2026-05-19T12:00:00+00:00",
  "producer": "service-name",
  "version": 1,
  "payload": {}
}
```

Гарантия доставки для всех событий: `at-least-once`.

## UserRegistered

| Поле | Значение |
|------|----------|
| Event name | `UserRegistered` |
| Routing key | `user.registered` |
| Producer | `user-service` |
| Consumers | `notification-service` |
| Delivery guarantee | `at-least-once` |

Payload:

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | integer | Идентификатор созданного пользователя |
| `login` | string | Логин пользователя |
| `first_name` | string | Имя пользователя |
| `last_name` | string | Фамилия пользователя |

Пример:

```json
{
  "event_id": "7b7e8d9d-91e0-4f6e-9a57-729fbf74bb15",
  "event_type": "UserRegistered",
  "occurred_at": "2026-05-19T12:00:00+00:00",
  "producer": "user-service",
  "version": 1,
  "payload": {
    "user_id": 1,
    "login": "Mikhail",
    "first_name": "Михаил",
    "last_name": "Копылов"
  }
}
```

## ProductCreated

| Поле | Значение |
|------|----------|
| Event name | `ProductCreated` |
| Routing key | `product.created` |
| Producer | `product-service` |
| Consumers | `notification-service` |
| Delivery guarantee | `at-least-once` |

Payload:

| Поле | Тип | Описание |
|------|-----|----------|
| `product_id` | integer | Идентификатор созданного товара |
| `name` | string | Название товара |
| `price` | number | Цена товара |
| `category` | string | Категория из расширенных атрибутов |
| `tags` | array[string] | Теги товара |

Пример:

```json
{
  "event_id": "f23986e5-4ac1-48cf-8a2a-5368a2d7d7f5",
  "event_type": "ProductCreated",
  "occurred_at": "2026-05-19T12:00:00+00:00",
  "producer": "product-service",
  "version": 1,
  "payload": {
    "product_id": 1,
    "name": "iPhone 15",
    "price": 79990.0,
    "category": "электроника",
    "tags": ["смартфон", "apple", "ios"]
  }
}
```
