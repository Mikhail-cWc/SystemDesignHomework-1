# Shop API — Домашнее задание 02

REST API интернет-магазина (вариант 2). Три микросервиса за Nginx API Gateway.

Архитектура описана в `workspace.dsl` (Structurizr DSL).

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| api-gateway | :80 | Nginx — единая точка входа |
| user-service | :8001 | Пользователи, JWT-аутентификация |
| product-service | :8002 | Каталог товаров |
| cart-service | :8003 | Корзина покупателя |

## Запуск

```bash
docker-compose up --build
```

Swagger UI после запуска:
- http://localhost:8001/docs — User Service
- http://localhost:8002/docs — Product Service
- http://localhost:8003/docs — Cart Service

## API Endpoints

| Метод | Путь | Сервис | Auth | Описание |
|-------|------|--------|------|----------|
| POST | /auth/register | User | — | Регистрация |
| POST | /auth/login | User | — | Вход |
| GET | /users/by-login?login= | User | JWT | Поиск по логину |
| GET | /users/search?q= | User | JWT | Поиск по маске имени/фамилии |
| POST | /products | Product | JWT | Создать товар |
| GET | /products | Product | — | Список товаров |
| GET | /products/{id} | Product | — | Товар по ID |
| POST | /cart/items | Cart | JWT | Добавить в корзину |
| GET | /cart | Cart | JWT | Получить корзину |

## Примеры

### Регистрация

```bash
curl -X POST http://localhost/auth/register \
  -H "Content-Type: application/json" \
  -d '{"login":"Mikhail","first_name":"Михаил","last_name":"Копылов","password":"pass123"}'
```

```json
{
  "id": 1,
  "login": "Mikhail",
  "first_name": "Михаил",
  "last_name": "Копылов",
  "access_token": "...",
  "token_type": "bearer"
}
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
curl "http://localhost/users/search?q=Jo" \
  -H "Authorization: Bearer $TOKEN"
```

### Создать товар

```bash
curl -X POST http://localhost/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"iPhone 15","description":"Apple smartphone","price":79990.00}'
```

### Список товаров

```bash
curl "http://localhost/products?skip=0&limit=20"
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

## Тесты

```bash
pip install -r tests/requirements-test.txt
python3 -m pytest tests/ -v
```

## Переменные окружения

| Переменная | Default | Описание |
|------------|---------|----------|
| JWT_SECRET | CHANGEME | Секрет для подписи JWT |
| JWT_ALGORITHM | HS256 | Алгоритм JWT |
| JWT_EXPIRE_MINUTES | 60 | Срок жизни токена (user-service) |
| PRODUCT_SERVICE_URL | http://product-service:8000 | URL product-service (cart-service) |
