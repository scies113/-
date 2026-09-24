"""Модуль работы с хранилищем данных в формате JSON.

Обеспечивает загрузку и сохранение графа объектов Product, Preserve, Batch
с автоматическим связыванием по идентификаторам и обработкой исключений.
"""

import json
from pathlib import Path
from typing import Any

from models.batches import Batch
from models.preserves import Preserve
from models.products import Product


def _read_json_file(filepath: str) -> list[dict[str, Any]]:
    """Вспомогательная функция безопасного чтения JSON-файла.

    :param filepath: Путь к файлу.
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


def _write_json_file(filepath: str, data: list[dict[str, Any]]) -> None:
    """Вспомогательная функция безопасной записи JSON-файла.

    :param filepath: Путь к файлу.
    :param data: Сериализуемые данные.
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_products(filepath: str) -> list[Product]:
    """Загружает коллекцию продуктов из JSON-файла.

    :param filepath: Путь к файлу products.json.
    :return: Список восстановленных объектов Product.
    """
    raw_data = _read_json_file(filepath)
    products: list[Product] = []
    for item in raw_data:
        try:
            products.append(Product.from_data(item))
        except (KeyError, ValueError, TypeError):
            continue
    return products


def save_products(filepath: str, products: list[Product]) -> None:
    """Сохраняет коллекцию продуктов в JSON-файл.

    :param filepath: Путь к файлу products.json.
    :param products: Список объектов Product.
    """
    data = [p.to_dict() for p in products]
    _write_json_file(filepath, data)


def load_preserves(
    filepath: str,
    products: list[Product],
) -> list[Preserve]:
    """Загружает заготовки из JSON со связыванием объектов Product.

    :param filepath: Путь к файлу preserves.json.
    :param products: Список доступных продуктов для связывания.
    :return: Список восстановленных объектов Preserve.
    """
    raw_data = _read_json_file(filepath)
    product_map = {p.id: p for p in products}
    preserves: list[Preserve] = []

    for item in raw_data:
        prod_id = item.get("product_id")
        product = product_map.get(prod_id)
        if product is None:
            continue
        try:
            preserves.append(Preserve.from_data(item, product))
        except (KeyError, ValueError, TypeError):
            continue
    return preserves


def save_preserves(filepath: str, preserves: list[Preserve]) -> None:
    """Сохраняет коллекцию заготовок в JSON-файл.

    :param filepath: Путь к файлу preserves.json.
    :param preserves: Список объектов Preserve.
    """
    data = [p.to_dict() for p in preserves]
    _write_json_file(filepath, data)


def load_batches(
    filepath: str,
    preserves: list[Preserve],
) -> list[Batch]:
    """Загружает партии из JSON со связыванием объектов Preserve.

    :param filepath: Путь к файлу batches.json.
    :param preserves: Список доступных заготовок для связывания.
    :return: Список восстановленных объектов Batch.
    """
    raw_data = _read_json_file(filepath)
    preserve_map = {p.id: p for p in preserves}
    batches: list[Batch] = []

    for item in raw_data:
        pres_id = item.get("preserve_id")
        preserve = preserve_map.get(pres_id)
        if preserve is None:
            continue
        try:
            batches.append(Batch.from_data(item, preserve))
        except (KeyError, ValueError, TypeError):
            continue
    return batches


def save_batches(filepath: str, batches: list[Batch]) -> None:
    """Сохраняет коллекцию партий в JSON-файл.

    :param filepath: Путь к файлу batches.json.
    :param batches: Список объектов Batch.
    """
    data = [b.to_dict() for b in batches]
    _write_json_file(filepath, data)
