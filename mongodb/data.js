// Тестовые данные для коллекции product_attrs
// Соответствует db/data.sql (products id 1-12)
// Запуск: mongosh ozon_shop < mongodb/data.js

db = db.getSiblingDB("ozon_shop");

db.product_attrs.drop();

db.product_attrs.insertMany([
  {
    product_id: "1",
    category: "электроника",
    tags: ["ноутбук", "lenovo", "учёба", "для работы"],
    images: ["https://cdn.ozon.ru/lenovo-ideapad.jpg"],
    attributes: {
      brand: "Lenovo",
      model: "IdeaPad 3",
      ram_gb: 8,
      storage_gb: 256,
      display_inch: 15.6,
      cpu: "Intel Core i5",
      os: "Windows 11"
    },
    rating: 4.2,
    review_count: 218,
    created_at: new Date("2024-01-10T10:00:00Z")
  },
  {
    product_id: "2",
    category: "электроника",
    tags: ["смартфон", "samsung", "android", "amoled"],
    images: ["https://cdn.ozon.ru/samsung-a54.jpg"],
    attributes: {
      brand: "Samsung",
      model: "Galaxy A54",
      ram_gb: 8,
      storage_gb: 128,
      display_inch: 6.4,
      os: "Android 14"
    },
    rating: 4.5,
    review_count: 634,
    created_at: new Date("2024-01-15T09:00:00Z")
  },
  {
    product_id: "3",
    category: "электроника",
    tags: ["наушники", "sony", "шумоподавление", "беспроводные"],
    images: ["https://cdn.ozon.ru/sony-wh1000.jpg"],
    attributes: {
      brand: "Sony",
      model: "WH-1000XM5",
      type: "накладные",
      connection: "Bluetooth 5.2",
      battery_hours: 30,
      noise_cancellation: true
    },
    rating: 4.8,
    review_count: 912,
    created_at: new Date("2024-02-01T08:00:00Z")
  },
  {
    product_id: "4",
    category: "электроника",
    tags: ["клавиатура", "механическая", "rgb", "игровая"],
    images: [],
    attributes: {
      type: "механическая",
      layout: "TKL",
      backlight: "RGB",
      switch_type: "Red"
    },
    rating: 4.3,
    review_count: 145,
    created_at: new Date("2024-02-10T12:00:00Z")
  },
  {
    product_id: "5",
    category: "электроника",
    tags: ["мышь", "logitech", "беспроводная", "для работы"],
    images: ["https://cdn.ozon.ru/mx-master3.jpg"],
    attributes: {
      brand: "Logitech",
      model: "MX Master 3",
      dpi: 4000,
      connection: "USB-C / Bluetooth",
      battery_hours: 70
    },
    rating: 4.9,
    review_count: 1103,
    created_at: new Date("2024-01-20T14:00:00Z")
  },
  {
    product_id: "6",
    category: "электроника",
    tags: ["монитор", "lg", "2k", "ips", "144гц"],
    images: ["https://cdn.ozon.ru/lg-27.jpg"],
    attributes: {
      brand: "LG",
      display_inch: 27,
      resolution: "2560x1440",
      panel: "IPS",
      refresh_hz: 144
    },
    rating: 4.7,
    review_count: 389,
    created_at: new Date("2024-01-25T11:00:00Z")
  },
  {
    product_id: "7",
    category: "электроника",
    tags: ["ssd", "samsung", "nvme", "накопитель"],
    images: [],
    attributes: {
      brand: "Samsung",
      capacity_gb: 1000,
      form_factor: "M.2 2280",
      interface: "NVMe PCIe 4.0",
      read_mbps: 3500,
      write_mbps: 3300
    },
    rating: 4.8,
    review_count: 562,
    created_at: new Date("2024-03-01T10:00:00Z")
  },
  {
    product_id: "8",
    category: "электроника",
    tags: ["камера", "logitech", "hd", "видеозвонки", "стрим"],
    images: ["https://cdn.ozon.ru/c920.jpg"],
    attributes: {
      brand: "Logitech",
      model: "C920",
      resolution: "1080p",
      fps: 30,
      autofocus: true,
      connection: "USB"
    },
    rating: 4.6,
    review_count: 278,
    created_at: new Date("2024-01-05T09:00:00Z")
  },
  {
    product_id: "9",
    category: "электроника",
    tags: ["зарядка", "usb-c", "gan", "быстрая зарядка"],
    images: [],
    attributes: {
      power_w: 65,
      technology: "GaN",
      ports: ["USB-C"],
      compatibility: ["ноутбуки", "смартфоны", "планшеты"]
    },
    rating: 4.4,
    review_count: 93,
    created_at: new Date("2024-01-08T10:00:00Z")
  },
  {
    product_id: "10",
    category: "электроника",
    tags: ["коврик", "xl", "аксессуар", "игровой"],
    images: [],
    attributes: {
      size: "900x400 мм",
      thickness_mm: 3,
      surface: "ткань",
      base: "резина"
    },
    rating: 4.5,
    review_count: 187,
    created_at: new Date("2024-01-08T10:00:00Z")
  },
  {
    product_id: "11",
    category: "электроника",
    tags: ["кабель", "hdmi", "4k", "8k"],
    images: [],
    attributes: {
      standard: "HDMI 2.1",
      length_m: 2,
      max_resolution: "8K 60Hz / 4K 144Hz",
      bandwidth_gbps: 48
    },
    rating: 4.3,
    review_count: 56,
    created_at: new Date("2024-03-05T15:00:00Z")
  },
  {
    product_id: "12",
    category: "электроника",
    tags: ["usb-хаб", "периферия", "usb3.0"],
    images: ["https://cdn.ozon.ru/usb-hub.jpg"],
    attributes: {
      ports: 7,
      standard: "USB 3.0",
      powered: true,
      connection: "USB-A"
    },
    rating: 4.2,
    review_count: 134,
    created_at: new Date("2024-03-05T15:00:00Z")
  }
]);

db.product_attrs.createIndex({ product_id: 1 }, { unique: true });
db.product_attrs.createIndex({ tags: 1 });
db.product_attrs.createIndex({ category: 1 });
db.product_attrs.createIndex({ rating: -1 });
