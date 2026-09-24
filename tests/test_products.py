"""Модульные тесты для класса Product и функций работы с продуктами."""

import pytest

from models.products import (
    Product,
    add_product,
    find_product_by_id,
    find_products_by_name,
)


def test_product_creation_and_str() -> None:
    """Проверка инициализации Product, атрибутов и метода __str__."""
    product = Product(product_id=1, name="Огурцы", category="овощи")
    assert product.id == 1
    assert product.name == "Огурцы"
    assert product.category == "овощи"
    assert str(product) == "[#1] Огурцы (Категория: овощи)"


def test_product_validate_name() -> None:
    """Проверка статического метода validate_name."""
    assert Product.validate_name("Огурцы") is True
    assert Product.validate_name("Томат") is True
    assert Product.validate_name("Я") is False
    assert Product.validate_name("") is False
    assert Product.validate_name("   ") is False


def test_product_invalid_name_raises() -> None:
    """Проверка выброса исключения при создании с невалидным именем."""
    with pytest.raises(ValueError):
        Product(product_id=1, name=" ", category="овощи")


def test_product_serialization() -> None:
    """Проверка сериализации в словарь и десериализации через from_data."""
    product = Product(product_id=2, name="Клубника", category="ягоды")
    data = product.to_dict()
    assert data == {"id": 2, "name": "Клубника", "category": "ягоды"}

    restored = Product.from_data(data)
    assert restored.id == product.id
    assert restored.name == product.name
    assert restored.category == product.category


def test_product_add_and_search() -> None:
    """Проверка добавления нового продукта и функций поиска."""
    products = [
        Product(product_id=1, name="Огурцы", category="овощи"),
        Product(product_id=2, name="Томаты", category="овощи"),
    ]
    new_product = add_product(products, "Малина", "ягоды")
    assert new_product.id == 3
    assert len(products) == 3

    found_by_id = find_product_by_id(products, 2)
    assert found_by_id is not None
    assert found_by_id.name == "Томаты"

    not_found = find_product_by_id(products, 99)
    assert not_found is None

    search_result = find_products_by_name(products, "ОГУР")
    assert len(search_result) == 1
    assert search_result[0].id == 1
