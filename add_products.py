from app import app
from models import db, Product

products = [
    {
        "name": "Basic Black T-Shirt",
        "description": "Классическая чёрная футболка на каждый день.",
        "price": 900,
        "category": "Футболки",
        "size": "S, M, L, XL",
        "image": ""
    },
    {
        "name": "White Oversize T-Shirt",
        "description": "Белая свободная футболка в стиле oversize.",
        "price": 1100,
        "category": "Футболки",
        "size": "M, L, XL",
        "image": ""
    },
    {
        "name": "Premium Hoodie Black",
        "description": "Чёрное тёплое худи с капюшоном.",
        "price": 2500,
        "category": "Худи",
        "size": "M, L, XL",
        "image": ""
    },
    {
        "name": "Grey Hoodie",
        "description": "Серое повседневное худи.",
        "price": 2300,
        "category": "Худи",
        "size": "S, M, L, XL",
        "image": ""
    },
    {
        "name": "Classic Blue Jeans",
        "description": "Синие джинсы классического кроя.",
        "price": 2800,
        "category": "Джинсы",
        "size": "29, 30, 32, 34",
        "image": ""
    },
    {
        "name": "Black Straight Jeans",
        "description": "Чёрные джинсы прямого кроя.",
        "price": 3000,
        "category": "Джинсы",
        "size": "30, 32, 34, 36",
        "image": ""
    },
    {
        "name": "Classic Black Pants",
        "description": "Классические чёрные брюки.",
        "price": 2600,
        "category": "Брюки",
        "size": "M, L, XL",
        "image": ""
    },
    {
        "name": "Cargo Pants",
        "description": "Повседневные брюки карго с карманами.",
        "price": 2900,
        "category": "Брюки",
        "size": "M, L, XL",
        "image": ""
    },
    {
        "name": "Winter Jacket",
        "description": "Тёплая зимняя куртка.",
        "price": 6500,
        "category": "Куртки",
        "size": "M, L, XL",
        "image": ""
    },
    {
        "name": "Light Bomber Jacket",
        "description": "Лёгкая куртка-бомбер для повседневного образа.",
        "price": 4500,
        "category": "Куртки",
        "size": "S, M, L, XL",
        "image": ""
    },
    {
        "name": "Classic Sneakers",
        "description": "Универсальные повседневные кроссовки.",
        "price": 4200,
        "category": "Обувь",
        "size": "40, 41, 42, 43, 44",
        "image": ""
    },
    {
        "name": "Sport Sneakers",
        "description": "Спортивные кроссовки для прогулок.",
        "price": 4800,
        "category": "Обувь",
        "size": "40, 41, 42, 43, 44",
        "image": ""
    },
    {
        "name": "Black Baseball Cap",
        "description": "Чёрная бейсболка с минималистичным дизайном.",
        "price": 700,
        "category": "Аксессуары",
        "size": "Универсальный",
        "image": ""
    },
    {
        "name": "Leather Belt",
        "description": "Классический ремень для брюк.",
        "price": 850,
        "category": "Аксессуары",
        "size": "Универсальный",
        "image": ""
    },
    {
        "name": "Classic Shirt",
        "description": "Мужская рубашка для повседневного и делового образа.",
        "price": 2200,
        "category": "Рубашки",
        "size": "M, L, XL",
        "image": ""
    }
]

with app.app_context():
    added = 0

    for item in products:
        existing = Product.query.filter_by(name=item["name"]).first()

        if existing:
            continue

        product = Product(**item)
        db.session.add(product)
        added += 1

    db.session.commit()

    print(f"Успешно добавлено товаров: {added}")
    print(f"Всего товаров в магазине: {Product.query.count()}")