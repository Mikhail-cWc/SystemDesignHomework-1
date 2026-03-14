workspace "Магазин (Ozon)" "Архитектура интернет-магазина, вариант по мотивам ozon.ru" {

    model {

        // Роли
        customer = person "Покупатель" "Зарегистрированный пользователь, который просматривает каталог, добавляет товары в корзину и оформляет заказы"
        admin = person "Администратор" "Сотрудник магазина, управляющий товарным каталогом"

        // Внешние системы
        paymentSystem = softwareSystem "Платёжная система" "Обрабатывает платежи покупателей" "External"
        emailService = softwareSystem "Сервис уведомлений" "Отправка уведомлений пользователям" "External"
        cdn = softwareSystem "CDN" "Хранение и раздача изображений товаров" "External"

        // Основная система
        ozonShop = softwareSystem "Магазин" "Интернет-магазин: пользователи, каталог товаров, корзина" {

            webApp = container "Web Application" "Пользовательский интерфейс магазина: просмотр каталога, управление корзиной, оформление заказа" "React, TypeScript" "Browser"

            apiGateway = container "API Gateway" "Единая точка входа: маршрутизация запросов, аутентификация по JWT, rate limiting" "Nginx" "Gateway"

            userService = container "User Service" "Управление пользователями: регистрация, поиск по логину, поиск по имени и фамилии. JWT-аутентификация, OpenAPI/Swagger" "Python, REST API"

            productService = container "Product Service" "Управление каталогом товаров: создание товаров, получение списка. OpenAPI/Swagger" "Python, REST API"

            cartService = container "Cart Service" "Управление корзиной: добавление товаров, получение корзины пользователя. OpenAPI/Swagger" "Python, REST API"

            usersDb = container "Users DB" "Хранит данные пользователей: логин, имя, фамилия, хэш пароля" "PostgreSQL" "Database"

            productsDb = container "Products DB" "Хранит каталог товаров: название, описание, цена, ссылка на изображение" "PostgreSQL" "Database"

            cartDb = container "Cart DB" "Хранит корзины пользователей: user_id, product_id, количество" "PostgreSQL" "Database"

            redis = container "Cache" "Кеширование: список товаров (TTL 10 мин), поиск пользователей (TTL 5 мин), корзина (TTL 30 мин), rate limiting" "Redis" "Cache"

            mongodb = container "Products MongoDB" "Документное хранилище расширенных атрибутов товаров (гибкая схема: характеристики, теги, вариации)" "MongoDB" "Database"

            messageBroker = container "Message Broker" "Шина событий: UserRegistered, ProductCreated, CartItemAdded. Гарантия доставки: at-least-once" "RabbitMQ" "MessageBroker"
        }

        // Отношения — System Context (C1)
        customer -> ozonShop "Просматривает каталог, добавляет товары в корзину, оформляет заказы" "HTTPS"
        admin -> ozonShop "Добавляет и редактирует товары в каталоге" "HTTPS"
        ozonShop -> paymentSystem "Проводит платежи" "HTTPS/REST"
        ozonShop -> emailService "Отправляет уведомления (регистрация, заказ)" "HTTPS/SMTP"
        ozonShop -> cdn "Загружает и отдаёт изображения товаров" "HTTPS"

        // Отношения — Container (C2)
        customer -> webApp "Открывает в браузере" "HTTPS"
        admin -> webApp "Открывает в браузере" "HTTPS"

        webApp -> apiGateway "Все API-запросы" "HTTPS/REST"

        apiGateway -> userService "Маршрутизация запросов пользователей" "HTTP/REST"
        apiGateway -> productService "Маршрутизация запросов каталога" "HTTP/REST"
        apiGateway -> cartService "Маршрутизация запросов корзины" "HTTP/REST"

        userService -> usersDb "Чтение и запись данных пользователей" "SQL"
        productService -> productsDb "Чтение и запись данных товаров" "SQL"
        cartService -> cartDb "Чтение и запись данных корзин" "SQL"

        cartService -> productService "Валидация существования товара перед добавлением в корзину" "HTTP/REST"

        userService -> emailService "Отправка письма при регистрации" "HTTPS/SMTP"
        productService -> cdn "Загрузка изображений товаров" "HTTPS"
        webApp -> cdn "Отображение изображений товаров" "HTTPS"

        apiGateway -> redis "Rate limiting по IP/userId, проверка JWT-сессий" "TCP"
        userService -> redis "Кеш результатов поиска пользователей (Cache-Aside)" "TCP"
        productService -> redis "Кеш списка товаров и отдельных товаров (Cache-Aside)" "TCP"
        cartService -> redis "Кеш корзины пользователя (Read-Through)" "TCP"

        productService -> mongodb "Чтение и запись расширенных атрибутов товаров" "MongoDB Driver/TCP"

        userService -> messageBroker "Публикует UserRegistered" "AMQP"
        productService -> messageBroker "Публикует ProductCreated" "AMQP"
        cartService -> messageBroker "Публикует CartItemAdded" "AMQP"
        messageBroker -> emailService "Доставляет события для отправки email-уведомлений" "AMQP/HTTPS"
    }

    views {

        systemContext ozonShop "SystemContext" "Диаграмма System Context (C1): система в контексте пользователей и внешних систем" {
            include *
            autoLayout
        }

        container ozonShop "Containers" "Диаграмма Container (C2): контейнеры системы и их взаимодействие" {
            include *
            autoLayout
        }

        dynamic ozonShop "UserRegistration" "Сценарий: Регистрация пользователя с event-driven уведомлением" {
            customer -> webApp "Заполняет форму регистрации"
            webApp -> apiGateway "POST /users {login, name, password}"
            apiGateway -> userService "POST /users {login, name, password}"
            userService -> usersDb "INSERT INTO users ..."
            usersDb -> userService "OK, userId"
            userService -> redis "Инвалидация кеша поиска по имени"
            userService -> messageBroker "Publish UserRegistered {userId, email}"
            messageBroker -> emailService "Consume UserRegistered → отправить приветственное письмо"
            userService -> apiGateway "201 Created {userId, token}"
            apiGateway -> webApp "201 Created {userId, token}"
            autoLayout
        }

        dynamic ozonShop "AddToCart" "Сценарий: Добавление товара в корзину покупателем" {
            customer -> webApp "Открывает страницу товара"
            webApp -> apiGateway "GET /products/{id}"
            apiGateway -> productService "GET /products/{id}"
            productService -> productsDb "SELECT * FROM products WHERE id = ?"
            productsDb -> productService "Данные товара"
            productService -> apiGateway "200 OK {product}"
            apiGateway -> webApp "200 OK {product}"
            customer -> webApp "Нажимает «Добавить в корзину»"
            webApp -> apiGateway "POST /cart/items {productId, quantity}"
            apiGateway -> cartService "POST /cart/items {userId, productId, quantity}"
            cartService -> productService "GET /products/{id} (валидация товара)"
            productService -> cartService "200 OK {product}"
            cartService -> cartDb "INSERT INTO cart_items (user_id, product_id, qty)"
            cartDb -> cartService "OK"
            cartService -> apiGateway "201 Created {cart}"
            apiGateway -> webApp "201 Created {cart}"
            autoLayout
        }

        styles {
            element "Person" {
                shape Person
                background #1168bd
                color #ffffff
            }
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #438dd5
                color #ffffff
            }
            element "Browser" {
                shape WebBrowser
            }
            element "Gateway" {
                shape Hexagon
            }
            element "Cache" {
                shape Ellipse
                background #ff9900
                color #ffffff
            }
            element "MessageBroker" {
                shape Pipe
                background #e63946
                color #ffffff
            }
        }

        theme default
    }
}
