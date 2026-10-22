-- DDL-скрипт создания схемы базы данных SQLite для системы учета домашних заготовок
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS preserves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    recipe_notes TEXT NOT NULL DEFAULT '',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    preserve_id INTEGER NOT NULL,
    production_date TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity >= 0),
    is_consumed INTEGER NOT NULL CHECK (is_consumed IN (0, 1)),
    FOREIGN KEY (preserve_id) REFERENCES preserves(id) ON DELETE RESTRICT
);
