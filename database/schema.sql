-- This schema creates all tables required for products, completed sales, and sale line items.

DROP TABLE IF EXISTS sale_items;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS products;

-- This table stores products available in the shop.
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    cost_price REAL NOT NULL CHECK (cost_price >= 0),
    sell_price REAL NOT NULL CHECK (sell_price >= 0),
    image_url TEXT NOT NULL
);

-- This table stores one completed sale per customer checkout.
CREATE TABLE sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    suburb TEXT NOT NULL,
    total_cost REAL NOT NULL,
    total_sell REAL NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- This table stores product-level details per sale so admin can see cost/sell per item.
CREATE TABLE sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    cost_price REAL NOT NULL,
    sell_price REAL NOT NULL,
    line_cost REAL NOT NULL,
    line_sell REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- This data seeds 15 products so the site exceeds the brief requirement of at least 10.
INSERT INTO products (id, title, description, category, cost_price, sell_price, image_url) VALUES
(1, 'Nightshade Leaf', 'Hand-picked at midnight from cursed hollows.', 'Herbs', 2.10, 4.99, 'images/nightshade-leaf.jpg'), --add jpgs in (or keep emoji placeholders)
(2, 'Dragons Tongue', 'Crimson herb found near dormant volcanic vents.', 'Herbs', 3.70, 7.99, 'images/dragons-tongue.jpg'),
(3, 'Moonbloom Petal', 'Delicate flower that blooms only under a full moon.', 'Herbs', 2.60, 5.99, 'images/moonbloom-petal.jpg'),
(4, 'Dragon Scale', 'Naturally shed scale from a mature fire dragon.', 'Creature Components', 16.00, 34.99, 'images/dragon-scale.jpg'),
(5, 'Basilisk Eye', 'Preserved eye with trace petrification properties.', 'Creature Components', 11.20, 22.99, 'images/basilisk-eye.jpg'),
(6, 'Griffin Feather', 'Gold-tipped feather gathered during molting season.', 'Creature Components', 9.40, 19.99, 'images/griffin-feather.jpg'),
(7, 'Obsidian Shard', 'Volcanic glass shard carrying residual shadow energy.', 'Minerals', 6.50, 12.99, 'images/obsidian-shard.jpg'),
(8, 'Mithril Dust', 'Finely ground ore that responds to magical intent.', 'Minerals', 12.80, 24.99, 'images/mithril-dust.jpg'),
(9, 'Sunstone Crystal', 'Amber gemstone that stores solar warmth.', 'Minerals', 7.80, 15.99, 'images/sunstone-crystal.jpg'),
(10, 'Venom of the Asp', 'Concentrated venom for controlled alchemical use.', 'Poisons & Potions', 8.20, 16.99, 'images/venom-of-the-asp.jpg'),
(11, 'Elixir of Strength', 'Burgundy elixir that grants temporary might.', 'Poisons & Potions', 10.50, 21.99, 'images/elixir-of-strength.jpg'),
(12, 'Potion of Invisibility', 'Clear brew rendering the drinker unseen temporarily.', 'Poisons & Potions', 19.50, 39.99, 'images/potion-of-invisibility.jpg'),
(13, 'Ether of Shadows', 'Distilled liquid from the umbral void.', 'Essences', 9.90, 18.99, 'images/ether-of-shadows.jpg'),
(14, 'Phoenix Flame Essence', 'Captured from a rebirth ember of a phoenix.', 'Essences', 15.10, 29.99, 'images/phoenix-flame-essence.jpg'),
(15, 'Aqua Vitae', 'Fabled restorative water drawn from an ancient spring.', 'Essences', 7.00, 14.99, 'images/aqua-vitae.jpg');

-- jpg images are placeholders and should be replaced with actual product images in the frontend
