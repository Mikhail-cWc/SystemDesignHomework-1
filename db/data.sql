INSERT INTO users (login, first_name, last_name, password_hash) VALUES
    ('ivanov',    'Иван',      'Иванов',    '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('petrov',    'Пётр',      'Петров',    '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('sidorova',  'Мария',     'Сидорова',  '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('kozlov',    'Алексей',   'Козлов',    '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('novikova',  'Елена',     'Новикова',  '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('sokolov',   'Дмитрий',   'Соколов',   '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('morozova',  'Анна',      'Морозова',  '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('volkov',    'Сергей',    'Волков',    '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('alekseeva', 'Ольга',     'Алексеева', '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('lebedev',   'Николай',   'Лебедев',   '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('smirnov',   'Андрей',    'Смирнов',   '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu'),
    ('kuznetsova','Татьяна',   'Кузнецова', '$2b$12$KIX1RrV1RrV1RrV1RrV1Ru1234567890abcdefghijklmnopqrstu');

INSERT INTO products (name, description, price, image_url) VALUES
    ('Ноутбук Lenovo IdeaPad 3',    'Ноутбук для работы и учёбы, 15.6", Intel Core i5', 49999.00, 'https://cdn.ozon.ru/lenovo-ideapad.jpg'),
    ('Смартфон Samsung Galaxy A54', 'Смартфон с AMOLED-экраном 6.4", 128 ГБ',           29999.00, 'https://cdn.ozon.ru/samsung-a54.jpg'),
    ('Беспроводные наушники Sony',  'Наушники с шумоподавлением WH-1000XM5',             24999.00, 'https://cdn.ozon.ru/sony-wh1000.jpg'),
    ('Клавиатура механическая',     'Игровая клавиатура с RGB-подсветкой',                3499.00, NULL),
    ('Мышь Logitech MX Master 3',  'Беспроводная мышь для профессионалов',               5999.00, 'https://cdn.ozon.ru/mx-master3.jpg'),
    ('Монитор LG 27"',              'IPS-монитор 2K, 144 Гц',                            21999.00, 'https://cdn.ozon.ru/lg-27.jpg'),
    ('SSD Samsung 1TB',             'Внутренний SSD M.2 NVMe, скорость чтения 3500 МБ/с', 6999.00, NULL),
    ('Веб-камера Logitech C920',    'HD-камера 1080p для видеозвонков',                   4299.00, 'https://cdn.ozon.ru/c920.jpg'),
    ('Зарядное устройство USB-C',   'Быстрая зарядка 65 Вт, GaN-технология',             1999.00, NULL),
    ('Коврик для мыши XL',          'Большой настольный коврик 900x400 мм',                799.00, NULL),
    ('Кабель HDMI 2.1 2м',          'Поддержка 4K 144 Гц и 8K 60 Гц',                    899.00, NULL),
    ('USB-хаб 7 портов',            'USB 3.0 хаб с отдельным питанием',                  2299.00, 'https://cdn.ozon.ru/usb-hub.jpg');

INSERT INTO cart_items (user_id, product_id, quantity) VALUES
    (1, 1, 1),
    (1, 5, 2),
    (1, 10, 1),
    (2, 2, 1),
    (2, 3, 1),
    (3, 4, 1),
    (3, 7, 2),
    (4, 6, 1),
    (5, 8, 1),
    (5, 9, 3),
    (6, 11, 2),
    (7, 12, 1),
    (8, 1, 1),
    (9, 2, 1),
    (10, 5, 1);

-- Генератор данных для НТ - добавляет 1001 пользователя, 501 товар и ~600 записей корзины
INSERT INTO users (login, first_name, last_name, password_hash)
SELECT
    'user_' || i,
    CASE (i % 10)
        WHEN 0 THEN 'Иван'
        WHEN 1 THEN 'Пётр'
        WHEN 2 THEN 'Мария'
        WHEN 3 THEN 'Алексей'
        WHEN 4 THEN 'Елена'
        WHEN 5 THEN 'Дмитрий'
        WHEN 6 THEN 'Анна'
        WHEN 7 THEN 'Сергей'
        WHEN 8 THEN 'Ольга'
        ELSE 'Андрей'
    END,
    CASE (i % 8)
        WHEN 0 THEN 'Иванов'
        WHEN 1 THEN 'Петров'
        WHEN 2 THEN 'Сидорова'
        WHEN 3 THEN 'Козлов'
        WHEN 4 THEN 'Новикова'
        WHEN 5 THEN 'Соколов'
        WHEN 6 THEN 'Морозова'
        ELSE 'Волков'
    END,
    '$2b$12$placeholder_hash_for_testing_only_not_real'
FROM generate_series(100, 1100) AS i;

INSERT INTO products (name, description, price)
SELECT
    'Товар #' || i,
    'Описание товара ' || i,
    (random() * 99000 + 1000)::numeric(12, 2)
FROM generate_series(100, 600) AS i;

INSERT INTO cart_items (user_id, product_id, quantity)
SELECT
    u.id,
    p.id,
    (random() * 4 + 1)::int
FROM
    (SELECT id FROM users ORDER BY id LIMIT 200) u
    CROSS JOIN LATERAL (
        SELECT id FROM products ORDER BY random() LIMIT 3
    ) p
ON CONFLICT ON CONSTRAINT uq_cart_user_product DO NOTHING;
