# Shop API — Домашние задания 03 и 04

REST API интернет-магазина (вариант 2). Три микросервиса за Nginx API Gateway.

**Хранилища данных**
- **PostgreSQL** — пользователи, базовые данные товаров, корзина
- **MongoDB** — расширенные атрибуты товаров (теги, характеристики, рейтинг)

Архитектура описана в `workspace.dsl` (Structurizr DSL).

## Схема базы данных

Единая PostgreSQL-база `shop`. Три таблицы:

### `users`

| Колонка | Тип | Ограничения |
|---------|-----|------------|
| id | SERIAL | PRIMARY KEY |
| login | VARCHAR(100) | NOT NULL, UNIQUE |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### `products`

| Колонка | Тип | Ограничения |
|---------|-----|------------|
| id | SERIAL | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | |
| price | NUMERIC(12,2) | NOT NULL, CHECK (price > 0) |
| image_url | TEXT | |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |

### `cart_items`

| Колонка | Тип | Ограничения |
|---------|-----|------------|
| id | SERIAL | PRIMARY KEY |
| user_id | INTEGER | NOT NULL, FK → users(id) ON DELETE CASCADE |
| product_id | INTEGER | NOT NULL, FK → products(id) ON DELETE CASCADE |
| quantity | INTEGER | NOT NULL, DEFAULT 1, CHECK (quantity > 0) |
| added_at | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() |
| — | — | UNIQUE(user_id, product_id) |

### Индексы

| Индекс | Тип | Назначение |
|--------|-----|-----------|
| `idx_users_login` | B-Tree (UNIQUE) | Поиск по логину |
| `idx_users_first_name_trgm` | GIN pg_trgm | ILIKE-поиск по имени |
| `idx_users_last_name_trgm` | GIN pg_trgm | ILIKE-поиск по фамилии |
| `idx_cart_items_user_id` | B-Tree | Получение корзины пользователя |
| `idx_cart_items_product_id` | B-Tree | JOIN cart_items → products |
| `idx_products_name` | B-Tree | Сортировка и фильтрация товаров |

## Файлы БД

| Файл | Описание |
|------|---------|
| `db/schema.sql` | CREATE TABLE + CREATE INDEX |
| `db/data.sql` | Тестовые данные (12 пользователей, 12 товаров, 15 записей корзины) |
| `db/queries.sql` | SQL для всех 7 API-операций |
| `db/optimization.md` | EXPLAIN ANALYZE до/после индексов |

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| api-gateway | :80 | Nginx — единая точка входа |
| user-service | :8001 | Пользователи, JWT-аутентификация |
| product-service | :8002 | Каталог товаров (PostgreSQL + MongoDB) |
| cart-service | :8003 | Корзина покупателя |
| postgres | :5432 | PostgreSQL 16 |
| mongodb | :27017 | MongoDB 7 — расширенные атрибуты товаров |

## Запуск

```bash
docker compose up --build -d
```

PostgreSQL инициализируется автоматически: при первом запуске выполняются `db/schema.sql` и `db/data.sql`.

Swagger UI после запуска:
- http://localhost:8001/docs — User Service
- http://localhost:8002/docs — Product Service
- http://localhost:8003/docs — Cart Service

### Подключение к PostgreSQL

```bash
docker exec -it systemdesignhomework-1-postgres-1 psql -U shop shop
```

### Ручной запуск SQL-скриптов

```bash
docker exec -i systemdesignhomework-1-postgres-1 psql -U shop shop < db/queries.sql
```

### Подключение к MongoDB

```bash
docker exec -it systemdesignhomework-1-mongodb-1 mongosh ozon_shop
```

### Загрузка тестовых данных MongoDB

```bash
# Валидация схемы + загрузка тестовых данных:
docker exec -i systemdesignhomework-1-mongodb-1 mongosh ozon_shop < mongodb/validation.js

# Только тестовые данные:
docker exec -i systemdesignhomework-1-mongodb-1 mongosh ozon_shop < mongodb/data.js

# CRUD-запросы и агрегации:
docker exec -i systemdesignhomework-1-mongodb-1 mongosh ozon_shop < mongodb/queries.js
```

## MongoDB — Файлы ДЗ 04

| Файл | Описание |
|------|---------|
| `mongodb/schema_design.md` | Документная модель, обоснование embedded/references, Polyglot Persistence |
| `mongodb/data.js` | Тестовые данные (10 документов: 4 электроника, 3 одежда, 3 книги) |
| `mongodb/queries.js` | CRUD-запросы: `$eq`, `$in`, `$ne`, `$gte`, `$lt`, `$and`, `$or`, `$push`, `$pull`, `$addToSet`, `$set` + aggregation pipeline |
| `mongodb/validation.js` | `$jsonSchema` валидация коллекции `product_attrs` + 5 тестов |

## API Endpoints

| Метод | Путь | Сервис | Auth | Описание |
|-------|------|--------|------|----------|
| POST | /auth/register | User | — | Регистрация |
| POST | /auth/login | User | — | Вход |
| GET | /users/by-login?login= | User | JWT | Поиск по логину |
| GET | /users/search?q= | User | JWT | Поиск по маске имени/фамилии |
| POST | /products | Product | JWT | Создать товар (PG + MongoDB) |
| GET | /products | Product | — | Список товаров (PG) |
| GET | /products?tags=смартфон | Product | — | Фильтр по тегам (MongoDB) |
| GET | /products/{id} | Product | — | Товар по ID (PG) |
| GET | /products/{id}?extended=true | Product | — | Товар + атрибуты (PG + MongoDB) |
| PUT | /products/{id}/attrs | Product | JWT | Обновить атрибуты (MongoDB) |
| DELETE | /products/{id} | Product | JWT | Удалить товар (PG + MongoDB) |
| POST | /cart/items | Cart | JWT | Добавить в корзину |
| GET | /cart | Cart | JWT | Получить корзину |

## Примеры

### Регистрация

```bash
curl -X POST http://localhost/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"Mikhail","first_name":"Михаил","last_name":"Копылов","password":"pass123"}'
```

### Вход и сохранение токена

```bash
TOKEN=$(curl -s -X POST http://localhost/auth/login \
  -H "Content-Type: application/json" \
  -d '{"login":"Mikhail","password":"pass123"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

### Поиск пользователя по логину

```bash
curl "http://localhost/users/by-login?login=Mikhail" \
  -H "Authorization: Bearer $TOKEN"
```

### Поиск по маске имени/фамилии

```bash
curl "http://localhost/users/search?q=Иван" \
  -H "Authorization: Bearer $TOKEN"
```

### Создать товар (dual-write: PostgreSQL + MongoDB)

```bash
curl -X POST http://localhost/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "iPhone 15",
    "description": "Apple smartphone",
    "price": 79990.00,
    "category": "электроника",
    "tags": ["смартфон", "apple", "ios"],
    "attributes": {"brand": "Apple", "ram_gb": 6, "storage_gb": 128},
    "images": ["https://cdn.ozon.ru/iphone15.jpg"]
  }'
```

### Список товаров (только PostgreSQL)

```bash
curl "http://localhost/products?skip=0&limit=20"
```

### Фильтр по тегам (MongoDB)

```bash
curl "http://localhost/products?tags=смартфон,apple"
```

### Товар с расширенными атрибутами (dual-read: PostgreSQL + MongoDB)

```bash
curl "http://localhost/products/1?extended=true"
```

### Обновить атрибуты товара (только MongoDB)

```bash
curl -X PUT http://localhost/products/1/attrs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"tags": ["смартфон", "apple", "хит продаж"], "attributes": {"brand": "Apple", "ram_gb": 6}}'
```

### Добавить в корзину

```bash
curl -X POST http://localhost/cart/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"product_id":1,"quantity":2}'
```

### Получить корзину

```bash
curl http://localhost/cart \
  -H "Authorization: Bearer $TOKEN"
```

## Переменные окружения

| Переменная | Default | Сервис | Описание |
|------------|---------|--------|----------|
| JWT_SECRET | CHANGEME | all | Секрет для подписи JWT |
| JWT_ALGORITHM | HS256 | all | Алгоритм JWT |
| JWT_EXPIRE_MINUTES | 60 | user | Срок жизни токена |
| DB_URL | postgresql://shop:shop@postgres:5432/shop | all | Строка подключения к PostgreSQL |
| MONGO_URL | mongodb://mongodb:27017 | product | Строка подключения к MongoDB |
| MONGO_DB_NAME | ozon_shop | product | Имя базы данных MongoDB |
