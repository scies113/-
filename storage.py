"""Модуль сохранения и загрузки данных в формате JSON (ПР2)."""

import json
from pathlib import Path


def load_json_data(filepath: str) -> list[dict]:
    """Загружает список словарей из JSON-файла с обработкой ошибок.

    :param filepath: Путь к файлу данных.
    :return: Список словарей или пустой список при ошибках чтения.
    """
    path = Path(filepath)
    if not path.is_file():
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json_data(filepath: str, data: list[dict]) -> None:
    """Сохраняет список словарей в JSON-файл с созданием директорий.

    :param filepath: Путь к файлу сохранения.
    :param data: Список сохраняемых словарей.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
