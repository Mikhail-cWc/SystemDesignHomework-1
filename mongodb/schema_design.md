# Проектирование документной модели MongoDB

| Хранилище | Данные | Причина |
|---|---|---|
| **PostgreSQL** (productsDb) | `id, name, description, price, image_url, is_available` | Структурированные поля, нужны для JOIN с таблицей `cart_items` |
| **MongoDB** (Products MongoDB) | Расширенные атрибуты: теги, характеристики, изображения, рейтинг | Гибкая схема — атрибуты различаются по категориям (электроника ≠ одежда ≠ книги) |

Пользователи и корзины остаются исключительно на PostgreSQL.

---

## Коллекции MongoDB

### Коллекция: `product_attrs`

Расширенные атрибуты товаров. Документ связан с записью в PostgreSQL через поле `product_id`.

```json
{
  "_id": ObjectId("..."),
  "product_id": "42",
  "category": "электроника",
  "tags": ["смартфон", "android", "samsung"],
  "images": [
    "https://cdn.ozon.ru/products/42/main.jpg",
    "https://cdn.ozon.ru/products/42/side.jpg"
  ],
  "attributes": {
    "brand": "Samsung",
    "model": "Galaxy S24",
    "ram_gb": 8,
    "storage_gb": 256,
    "color": "черный",
    "display_inch": 6.2
  },
  "rating": 4.7,
  "review_count": 312,
  "created_at": ISODate("2024-01-15T10:00:00Z")
}
```

**Гибкая схема `attributes` по категориям:**

| Категория | Поля attributes |
|---|---|
| электроника | `brand, model, ram_gb, storage_gb, color, display_inch` |
| одежда | `brand, sizes (array), material, color` |
| книги | `author, publisher, pages, isbn, language` |
| дом | `brand, material, dimensions, weight_kg` |
| спорт | `brand, sport_type, sizes (array), material` |

---

## Обоснование выбора Embedded vs References

### `product_attrs.attributes` — **Embedded document**

**Выбор:** Embedded

**Причина:**
- Атрибуты всегда читаются вместе с документом (нет смысла делать отдельный запрос)
- Схема гибкая и варьируется по категориям — именно для этого MongoDB идеален
- Нет необходимости обращаться к атрибутам независимо от товара

### `product_attrs.tags` — **Embedded array**

**Выбор:** Embedded

**Причина:**
- Небольшой список (обычно 3–10 тегов), не растёт неограниченно
- Операции `$push`, `$pull`, `$addToSet` работают прямо на массиве
- Поиск `{ tags: { $in: [...] } }` эффективен с индексом на поле `tags`
- Вынос в отдельную коллекцию усложнил бы модель без ощутимой выгоды

### `product_attrs.images` — **Embedded array**

**Выбор:** Embedded

**Причина:**
- Изображения — это ссылки на CDN, читаются вместе со страницей товара
- Список конечный (обычно до 10 штук)
- Нет независимого доступа к изображениям вне контекста товара

### `product_attrs.product_id` — **Reference (→ PostgreSQL)**

**Выбор:** Reference

**Причина:**
- `product_id` — первичный ключ из PostgreSQL; MongoDB документ — расширение основной записи
- Связь между двумя БД через строковый ключ — стандартный подход Polyglot Persistence
- При удалении товара из PostgreSQL необходимо явно удалять документ из MongoDB

---

## Индексы

```js
db.product_attrs.createIndex({ product_id: 1 }, { unique: true })
db.product_attrs.createIndex({ tags: 1 })
db.product_attrs.createIndex({ category: 1 })
db.product_attrs.createIndex({ rating: -1 })
```

- `product_id` (unique) — основной способ поиска документа при dual-read
- `tags` — multikey-индекс для `$in`-запросов по тегам
- `category` — фильтрация по категории
- `rating` — сортировка по рейтингу

---

## Как работают API-эндпоинты (dual-write / dual-read)

```
POST /products
  → INSERT INTO products (name, description, price, image_url) → postgres → product_id
  → db.product_attrs.insertOne({ product_id, category, tags, attributes, ... }) → mongodb
  → вернуть объединённый ProductExtended

GET /products                     → только PostgreSQL (быстрый список)
GET /products?tags=смартфон       → MongoDB find({ tags: {$in} }) + JOIN postgres
GET /products/{id}                → только PostgreSQL
GET /products/{id}?extended=true  → PostgreSQL + MongoDB, объединить
PUT /products/{id}/attrs          → только MongoDB updateOne
DELETE /products/{id}             → PostgreSQL deleteOne + MongoDB deleteOne
```
