# Event-Driven Architecture Design

## Цель

Добавить минимальную событийно-ориентированную архитектуру в существующий Shop API. Система сохраняет текущие REST API и синхронные записи в PostgreSQL/MongoDB, а после успешных команд публикует доменные события в RabbitMQ.

Реализованы два события:

| Событие | Команда | Producer |
|---------|---------|----------|
| `UserRegistered` | `POST /auth/register` | `user-service` |
| `ProductCreated` | `POST /products` | `product-service` |

## Выбор брокера

Выбран RabbitMQ, потому что для текущей системы нужны простая публикация событий, маршрутизация по типам событий и демонстрация exchange/routing. Kafka больше подходит для долговременного event log и потоковой аналитики, что было бы избыточно для этого проекта.

RabbitMQ topology:

| Компонент | Значение |
|-----------|----------|
| Exchange | `shop.events` |
| Exchange type | `topic` |
| Queue | `notifications.queue` |
| Routing keys | `user.registered`, `product.created` |

## Producers и Consumers

`user-service` публикует `UserRegistered` после успешной записи пользователя в PostgreSQL.

`product-service` публикует `ProductCreated` после успешного dual-write товара в PostgreSQL и MongoDB и после инвалидации кеша каталога.

`notification-service` подписан на оба routing key. В учебной реализации consumer логирует полученные события и подтверждает их через manual ack. В production-версии этот сервис **мог бы** отправлять email, push-уведомления или передавать события во внешнюю систему аналитики.

## Формат события

Все события используют общий envelope:

```json
{
  "event_id": "uuid",
  "event_type": "UserRegistered",
  "occurred_at": "2026-05-19T12:00:00+00:00",
  "producer": "user-service",
  "version": 1,
  "payload": {}
}
```

`event_id` нужен для идемпотентности consumers. `version` позволяет развивать схему события без изменения имени события.

## Гарантии доставки

Используется гарантия `at-least-once`:

- durable exchange `shop.events`;
- durable queue `notifications.queue`;
- persistent messages;
- manual ack после обработки сообщения;
- `nack(requeue=True)` при ошибке обработки.

При `at-least-once` возможна повторная доставка события, поэтому реальные consumers должны быть идемпотентны по `event_id`. В текущей реализации consumer только логирует события, поэтому повторная обработка не меняет состояние системы.

Если RabbitMQ временно недоступен во время публикации, основная REST-команда не откатывается.

## CQRS

CQRS применим к каталогу товаров. Текущая write model находится в PostgreSQL и MongoDB: `POST /products` создает базовые данные товара и расширенные атрибуты. Событие `ProductCreated` может асинхронно обновлять read model каталога, например отдельную MongoDB-коллекцию или поисковый индекс.

Отдельная read model не создается. `notification-service` демонстрирует consumer-механику.
