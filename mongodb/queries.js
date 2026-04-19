// MongoDB CRUD-запросы для коллекции product_attrs
// Запуск: mongosh ozon_shop < mongodb/queries.js

db = db.getSiblingDB("ozon_shop");


// Вставка нового документа
db.product_attrs.insertOne({
  product_id: "99",
  category: "электроника",
  tags: ["планшет", "apple", "новинка"],
  images: ["https://cdn.ozon.ru/products/99/main.jpg"],
  attributes: {
    brand: "Apple",
    model: "iPad Air M2",
    ram_gb: 8,
    storage_gb: 128,
    color: "синий",
    display_inch: 11.0
  },
  rating: Double(0),
  review_count: Int32(0),
  created_at: new Date()
});

print("insertOne: OK");


// Поиск по product_id ($eq)
printjson(db.product_attrs.findOne({ product_id: { $eq: "1" } }));

// Поиск по тегу ($in)
print("\nТовары с тегами 'смартфон' или 'ноутбук':");
db.product_attrs.find({ tags: { $in: ["смартфон", "ноутбук"] } }).forEach(d =>
  print(`  ${d.product_id}: ${d.attributes.brand} ${d.attributes.model}`)
);

// Фильтр: рейтинг >= 4.5 И категория = электроника ($and, $gte)
print("\nЭлектроника с рейтингом >= 4.5:");
db.product_attrs.find({
  $and: [
    { category: "электроника" },
    { rating: { $gte: 4.5 } }
  ]
}).forEach(d => print(`  product_id=${d.product_id}, rating=${d.rating}`));

// Категория одна из нескольких ($in)
print("\nКатегории 'одежда' и 'спорт':");
db.product_attrs.find({ category: { $in: ["одежда", "спорт"] } })
  .forEach(d => print(`  product_id=${d.product_id}, category=${d.category}`));

// Исключить уценённые ($ne)
print("\nТовары без тега 'уценённый':");
db.product_attrs.find({ tags: { $ne: "уценённый" } })
  .forEach(d => print(`  product_id=${d.product_id}`));

// Цена: товары с review_count < 200 ($lt)
print("\nТовары с менее 200 отзывами:");
db.product_attrs.find({ review_count: { $lt: 200 } })
  .forEach(d => print(`  product_id=${d.product_id}, review_count=${d.review_count}`));

// OR: книги или рейтинг > 4.8 ($or, $gt)
print("\nКниги ИЛИ рейтинг > 4.8:");
db.product_attrs.find({
  $or: [
    { category: "книги" },
    { rating: { $gt: 4.8 } }
  ]
}).forEach(d => print(`  product_id=${d.product_id}, category=${d.category}, rating=${d.rating}`));


// Добавить тег ($addToSet — не дублирует)
db.product_attrs.updateOne(
  { product_id: "2" },
  { $addToSet: { tags: "хит продаж" } }
);
print("addToSet 'хит продаж' к product_id=2: OK");

// Удалить тег ($pull)
db.product_attrs.updateOne(
  { product_id: "1" },
  { $pull: { tags: "хит продаж" } }
);
print("pull 'хит продаж' из product_id=1: OK");

// Добавить изображение ($push)
db.product_attrs.updateOne(
  { product_id: "3" },
  { $push: { images: "https://cdn.ozon.ru/products/3/keyboard.jpg" } }
);
print("push нового изображения к product_id=3: OK");

// Обновить рейтинг и счётчик отзывов ($set)
db.product_attrs.updateOne(
  { product_id: "5" },
  { $set: { rating: 4.9, review_count: 600 } }
);
print("set rating=4.9 для product_id=5: OK");


// Удаление тестового документа
db.product_attrs.deleteOne({ product_id: "99" });
print("deleteOne product_id=99: OK");


db.product_attrs.aggregate([
  { $match: { rating: { $gt: 0 } } },
  {
    $group: {
      _id: "$category",
      avg_rating: { $avg: "$rating" },
      total_reviews: { $sum: "$review_count" },
      product_count: { $sum: 1 }
    }
  },
  { $sort: { avg_rating: -1 } },
  {
    $project: {
      _id: 0,
      category: "$_id",
      avg_rating: { $round: ["$avg_rating", 2] },
      total_reviews: 1,
      product_count: 1
    }
  }
]).forEach(r => printjson(r));

print("\nВсе запросы выполнены.");
