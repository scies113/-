"""Модуль подключения к базе данных SQLite."""

from pathlib import Path
import sqlite3
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "preserves.sqlite"


def get_connection(
    custom_path: Optional[Path] = None,
) -> sqlite3.Connection:
    """Создает и настраивает подключение к SQLite.

    Включает row_factory = sqlite3.Row для доступа к полям по именам
    и активирует поддержку внешних ключей (foreign keys).

    :param custom_path: Необязательный пользовательский путь к файлу БД.
    :return: Настроенный объект подключения sqlite3.Connection.
    """
    target_path = custom_path if custom_path is not None else DB_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
