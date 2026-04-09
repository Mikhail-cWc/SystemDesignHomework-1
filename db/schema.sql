CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    login         VARCHAR(100) NOT NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_users_login UNIQUE (login)
);

CREATE TABLE IF NOT EXISTS products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255)   NOT NULL,
    description TEXT,
    price       NUMERIC(12, 2) NOT NULL,
    image_url   TEXT,
    created_at  TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_products_price CHECK (price > 0)
);

CREATE TABLE IF NOT EXISTS cart_items (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER     NOT NULL,
    product_id INTEGER     NOT NULL,
    quantity   INTEGER     NOT NULL DEFAULT 1,
    added_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_cart_user    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    CONSTRAINT fk_cart_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_user_product UNIQUE (user_id, product_id),
    CONSTRAINT chk_cart_quantity    CHECK (quantity > 0)
);

-- Индекс для поиска пользователя по логину (WHERE login = $1)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_login
    ON users (login);

-- Индексы для поиска пользователя по маске имени/фамилии (ILIKE)
-- Используется расширение pg_trgm для поддержки LIKE/ILIKE с индексом
CREATE INDEX IF NOT EXISTS idx_users_first_name_trgm
    ON users USING GIN (first_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_users_last_name_trgm
    ON users USING GIN (last_name gin_trgm_ops);

-- Индекс для FK и выборки корзины конкретного пользователя (WHERE user_id = $1)
CREATE INDEX IF NOT EXISTS idx_cart_items_user_id
    ON cart_items (user_id);

-- Индекс для FK на product_id (используется при JOIN с products)
CREATE INDEX IF NOT EXISTS idx_cart_items_product_id
    ON cart_items (product_id);

-- Индекс для сортировки и фильтрации товаров по имени
CREATE INDEX IF NOT EXISTS idx_products_name
    ON products (name);
