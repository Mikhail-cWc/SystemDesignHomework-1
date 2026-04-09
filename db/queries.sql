-- ============================================================
-- SQL-запросы для всех операций варианта 2 (Магазин / Ozon)
-- ============================================================

-- 1. Создание нового пользователя
--    Возвращает созданную запись; при дублировании login выбрасывает ошибку (uq_users_login)
INSERT INTO users (login, first_name, last_name, password_hash)
VALUES ($1, $2, $3, $4)
RETURNING id, login, first_name, last_name, created_at;

-- 2. Поиск пользователя по логину
--    Используется индекс idx_users_login (Unique Index Scan)
SELECT id, login, first_name, last_name, created_at
FROM users
WHERE login = $1;

-- 3. Поиск пользователя по маске имени и фамилии
--    $1 — маска, например '%Ива%'
--    Используются GIN-индексы idx_users_first_name_trgm и idx_users_last_name_trgm
SELECT id, login, first_name, last_name, created_at
FROM users
WHERE first_name ILIKE $1
   OR last_name  ILIKE $1;

-- 4. Создание товара
INSERT INTO products (name, description, price, image_url)
VALUES ($1, $2, $3, $4)
RETURNING id, name, description, price, image_url, created_at;

-- 5. Получение списка товаров (с пагинацией)
--    $1 = limit, $2 = offset
--    Используется индекс idx_products_name для сортировки без Seq Scan
SELECT id, name, description, price, image_url
FROM products
ORDER BY id
LIMIT $1 OFFSET $2;

-- 6. Добавление товара в корзину
--    Если товар уже есть — увеличиваем quantity
--    $1 = user_id, $2 = product_id, $3 = quantity
INSERT INTO cart_items (user_id, product_id, quantity)
VALUES ($1, $2, $3)
ON CONFLICT ON CONSTRAINT uq_cart_user_product
DO UPDATE SET quantity = cart_items.quantity + EXCLUDED.quantity
RETURNING id, user_id, product_id, quantity, added_at;

-- 7. Получение корзины пользователя с данными о товарах
--    $1 = user_id
--    Используется idx_cart_items_user_id (Index Scan) + idx_cart_items_product_id (FK-join)
SELECT
    ci.id,
    ci.product_id,
    p.name        AS product_name,
    p.price       AS product_price,
    ci.quantity,
    p.price * ci.quantity AS item_total
FROM cart_items ci
JOIN products p ON p.id = ci.product_id
WHERE ci.user_id = $1
ORDER BY ci.added_at;
