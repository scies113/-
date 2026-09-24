"""Модульные тесты для класса Preserve и функций работы с заготовками."""

import pytest

from models.preserves import (
    Preserve,
    add_preserve,
    filter_preserves_by_product,
    find_preserve_by_id,
)
from models.products import Product


def test_preserve_creation_and_str() -> None:
    """Проверка создания Preserve, связи с Product и метода __str__."""
    product = Product(product_id=1, name="Огурцы", category="овощи")
    preserve = Preserve(
        preserve_id=1,
        name="Маринованные огурцы",
        product=product,
        recipe_notes="С укропом и чесноком",
    )

    assert preserve.id == 1
    assert preserve.name == "Маринованные огурцы"
    assert preserve.product is product
    assert preserve.product.name == "Огурцы"
    assert str(preserve) == (
        "[#1] Заготовка: 'Маринованные огурцы' (Основной продукт: Огурцы)"
    )


def test_preserve_type_error_on_invalid_product() -> None:
    """Проверка ошибки при передаче неверного типа продукта."""
    with pytest.raises(TypeError):
        Preserve(  # type: ignore
            preserve_id=1,
            name="Варенье",
            product="Клубника",
        )


def test_preserve_serialization() -> None:
    """Проверка сериализации в словарь и десериализации Preserve."""
    product = Product(product_id=3, name="Клубника", category="ягоды")
    preserve = Preserve(
        preserve_id=5,
        name="Клубничное варенье",
        product=product,
        recipe_notes="Пятиминутка",
    )
    data = preserve.to_dict()
    assert data == {
        "id": 5,
        "name": "Клубничное варенье",
        "product_id": 3,
        "recipe_notes": "Пятиминутка",
    }

    restored = Preserve.from_data(data, product)
    assert restored.id == preserve.id
    assert restored.name == preserve.name
    assert restored.product.id == product.id
    assert restored.recipe_notes == preserve.recipe_notes


def test_preserve_functions() -> None:
    """Проверка добавления заготовки, поиска по ID и фильтрации по сырью."""
    prod_cucumber = Product(product_id=1, name="Огурцы", category="овощи")
    prod_tomato = Product(product_id=2, name="Томаты", category="овощи")

    preserves = [
        Preserve(1, "Огурцы малосольные", prod_cucumber),
        Preserve(2, "Томаты в соку", prod_tomato),
    ]

    new_item = add_preserve(
        preserves,
        "Огурцы маринованные",
        prod_cucumber,
        "Острые",
    )
    assert new_item.id == 3
    assert len(preserves) == 3

    found = find_preserve_by_id(preserves, 2)
    assert found is not None
    assert found.name == "Томаты в соку"

    filtered = filter_preserves_by_product(preserves, prod_cucumber.id)
    assert len(filtered) == 2
    assert all(p.product.id == 1 for p in filtered)
