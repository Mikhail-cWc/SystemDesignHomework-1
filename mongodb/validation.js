// Валидация схем для коллекции product_attrs
// Запуск: mongosh ozon_shop < mongodb/validation.js

db = db.getSiblingDB("ozon_shop");

db.product_attrs.drop();

db.createCollection("product_attrs", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["product_id", "category", "tags", "created_at"],
      additionalProperties: true,
      properties: {
        product_id: {
          bsonType: "string",
          description: "ID товара из PostgreSQL — обязательное строковое поле"
        },
        category: {
          bsonType: "string",
          enum: ["электроника", "одежда", "книги", "дом", "спорт"],
          description: "Категория товара — одно из допустимых значений"
        },
        tags: {
          bsonType: "array",
          minItems: 1,
          items: { bsonType: "string" },
          description: "Массив строковых тегов — минимум один тег"
        },
        images: {
          bsonType: "array",
          items: { bsonType: "string" },
          description: "Ссылки на изображения"
        },
        attributes: {
          bsonType: "object",
          description: "Расширенные атрибуты — гибкая схема по категории"
        },
        rating: {
          bsonType: "double",
          minimum: 0.0,
          maximum: 5.0,
          description: "Рейтинг товара от 0.0 до 5.0"
        },
        review_count: {
          bsonType: "int",
          minimum: 0,
          description: "Количество отзывов — неотрицательное целое"
        },
        created_at: {
          bsonType: "date",
          description: "Дата создания записи"
        }
      }
    }
  },
  validationAction: "error",
  validationLevel: "strict"
});

print("Коллекция product_attrs создана с валидатором $jsonSchema.");

db.product_attrs.createIndex({ product_id: 1 }, { unique: true });
db.product_attrs.createIndex({ tags: 1 });
db.product_attrs.createIndex({ category: 1 });
db.product_attrs.createIndex({ rating: -1 });

print("Индексы созданы.");

try {
  db.product_attrs.insertOne({
    product_id: "test-valid",
    category: "электроника",
    tags: ["тест"],
    attributes: { brand: "Test" },
    rating: 4.5,
    review_count: 10,
    created_at: new Date()
  });
  print("OK: Валидный документ вставлен.");
} catch (e) {
  print("FAIL: " + e.message);
}

try {
  db.product_attrs.insertOne({
    product_id: "test-bad-rating",
    category: "электроника",
    tags: ["тест"],
    rating: 6.0,
    review_count: 0,
    created_at: new Date()
  });
  print("FAIL: Документ с rating=6.0 вставился (не должен был).");
} catch (e) {
  print("OK: Валидация сработала — " + e.message.substring(0, 80) + "...");
}

try {
  db.product_attrs.insertOne({
    category: "книги",
    tags: ["тест"],
    created_at: new Date()
  });
  print("FAIL: Документ без product_id вставился (не должен был).");
} catch (e) {
  print("OK: Валидация сработала — " + e.message.substring(0, 80) + "...");
}

try {
  db.product_attrs.insertOne({
    product_id: "test-bad-cat",
    category: "авиация",
    tags: ["тест"],
    created_at: new Date()
  });
  print("FAIL: Документ с category='авиация' вставился (не должен был).");
} catch (e) {
  print("OK: Валидация сработала — " + e.message.substring(0, 80) + "...");
}

try {
  db.product_attrs.insertOne({
    product_id: "test-empty-tags",
    category: "одежда",
    tags: [],
    created_at: new Date()
  });
  print("FAIL: Документ с пустыми tags вставился (не должен был).");
} catch (e) {
  print("OK: Валидация сработала — " + e.message.substring(0, 80) + "...");
}

db.product_attrs.deleteOne({ product_id: "test-valid" });

print("\nВалидация протестирована. Запустите mongodb/data.js для загрузки тестовых данных:")
print("  docker exec -i <mongo-container> mongosh ozon_shop < mongodb/data.js");
