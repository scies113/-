"""Скрипт первоначального импорта данных из JSON в базу данных SQLite."""

import json
from pathlib import Path
from typing import Any

from db.database import DB_PATH, get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SQL_DIR = BASE_DIR / "sql"
SCHEMA_PATH = SQL_DIR / "schema.sql"

PRODUCTS_JSON = DATA_DIR / "products.json"
PRESERVES_JSON = DATA_DIR / "preserves.json"
BATCHES_JSON = DATA_DIR / "batches.json"


def _read_json(filepath: Path) -> list[dict[str, Any]]:
    """Безопасное чтение данных из JSON-файла."""
    if not filepath.is_file():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return []


def init_db(schema_path: Path = SCHEMA_PATH) -> None:
    """Инициализирует структуру БД на основе DDL схемы."""
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        conn.execute("DROP TABLE IF EXISTS batches;")
        conn.execute("DROP TABLE IF EXISTS preserves;")
        conn.execute("DROP TABLE IF EXISTS products;")
        conn.executescript(schema_sql)
        conn.execute("PRAGMA foreign_keys = ON;")


def import_data() -> None:
    """Импортирует данные из JSON-файлов в таблицы SQLite."""
    init_db()

    raw_products = _read_json(PRODUCTS_JSON)
    raw_preserves = _read_json(PRESERVES_JSON)
    raw_batches = _read_json(BATCHES_JSON)

    products_rows = [
        (
            item["id"],
            str(item["name"]).strip(),
            str(item["category"]).strip(),
        )
        for item in raw_products
    ]

    preserves_rows = [
        (
            item["id"],
            str(item["name"]).strip(),
            int(item["product_id"]),
            str(item.get("recipe_notes", "")).strip(),
        )
        for item in raw_preserves
    ]

    batches_rows = [
        (
            item["id"],
            int(item["preserve_id"]),
            str(item["production_date"]).strip(),
            int(item["quantity"]),
            1 if item.get("is_consumed", False) else 0,
        )
        for item in raw_batches
    ]

    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        insert_prod_sql = (
            "INSERT INTO products (id, name, category) VALUES (?, ?, ?);"
        )
        conn.executemany(insert_prod_sql, products_rows)

        insert_pres_sql = (
            "INSERT INTO preserves (id, name, product_id, recipe_notes) "
            "VALUES (?, ?, ?, ?);"
        )
        conn.executemany(insert_pres_sql, preserves_rows)

        insert_batch_sql = (
            "INSERT INTO batches (id, preserve_id, production_date, quantity, "
            "is_consumed) VALUES (?, ?, ?, ?, ?);"
        )
        conn.executemany(insert_batch_sql, batches_rows)

        conn.commit()

    print(
        f"Импорт успешно завершен в {DB_PATH}:\n"
        f"  - Продуктов: {len(products_rows)}\n"
        f"  - Заготовок: {len(preserves_rows)}\n"
        f"  - Партий: {len(batches_rows)}"
    )


if __name__ == "__main__":
    import_data()
