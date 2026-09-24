"""Модульные тесты для класса Batch и функций управления партиями."""

import pytest

from models.batches import (
    Batch,
    consume_from_batch,
    create_batch,
    find_batch_by_id,
    get_active_batches,
    get_batch_status,
    sort_batches_by_date,
)
from models.preserves import Preserve
from models.products import Product


@pytest.fixture
def sample_preserve() -> Preserve:
    """Фикстура для создания объекта Preserve со связанным Product."""
    product = Product(product_id=1, name="Огурцы", category="овощи")
    return Preserve(
        preserve_id=1,
        name="Маринованные огурцы",
        product=product,
    )


def test_batch_creation_and_links(sample_preserve: Preserve) -> None:
    """Проверка создания Batch, ссылок на Preserve и Product, статуса."""
    batch = Batch(
        batch_id=1,
        preserve=sample_preserve,
        production_date="2026-09-10",
        quantity=8,
    )
    assert batch.id == 1
    assert batch.preserve is sample_preserve
    assert batch.preserve.product.name == "Огурцы"
    assert batch.quantity == 8
    assert batch.is_consumed is False
    assert "8 шт. [АКТИВНА]" in str(batch)


def test_batch_consume_partial(sample_preserve: Preserve) -> None:
    """Успешное списание части банок методом consume()."""
    batch = Batch(
        batch_id=1,
        preserve=sample_preserve,
        production_date="2026-09-10",
        quantity=10,
    )
    success = batch.consume(4)
    assert success is True
    assert batch.quantity == 6
    assert batch.is_consumed is False


def test_batch_consume_full(sample_preserve: Preserve) -> None:
    """Полное списание банок с переключением is_consumed = True."""
    batch = Batch(
        batch_id=1,
        preserve=sample_preserve,
        production_date="2026-09-10",
        quantity=5,
    )
    success = batch.consume(5)
    assert success is True
    assert batch.quantity == 0
    assert batch.is_consumed is True
    assert "[ИЗРАСХОДОВАНА]" in str(batch)


def test_batch_consume_overflow(sample_preserve: Preserve) -> None:
    """Отказ при попытке списать больше банок, чем имеется в наличии."""
    batch = Batch(
        batch_id=1,
        preserve=sample_preserve,
        production_date="2026-09-10",
        quantity=3,
    )
    success = batch.consume(10)
    assert success is False
    assert batch.quantity == 3
    assert batch.is_consumed is False

    invalid_amount = batch.consume(-1)
    assert invalid_amount is False


def test_batch_sort_by_date(sample_preserve: Preserve) -> None:
    """Сортировка партий по дате с использованием lambda-функции."""
    b1 = Batch(1, sample_preserve, "2026-09-01", 5)
    b2 = Batch(2, sample_preserve, "2026-09-15", 10)
    b3 = Batch(3, sample_preserve, "2026-08-20", 3)

    batches = [b1, b2, b3]
    sorted_desc = sort_batches_by_date(batches, reverse=True)
    assert [b.id for b in sorted_desc] == [2, 1, 3]

    sorted_asc = sort_batches_by_date(batches, reverse=False)
    assert [b.id for b in sorted_asc] == [3, 1, 2]


def test_batch_validate_quantity() -> None:
    """Проверка статического метода validate_quantity."""
    assert Batch.validate_quantity(10) is True
    assert Batch.validate_quantity(0) is True
    assert Batch.validate_quantity(-1) is False
    assert Batch.validate_quantity("10") is False  # type: ignore
    assert Batch.validate_quantity(True) is False  # type: ignore


def test_batch_get_active_and_status(sample_preserve: Preserve) -> None:
    """Проверка получения активных партий и статуса."""
    b1 = Batch(1, sample_preserve, "2026-09-01", 5)
    b2 = Batch(2, sample_preserve, "2026-09-02", 0)

    batches = [b1, b2]
    active = get_active_batches(batches)
    assert len(active) == 1
    assert active[0].id == 1

    assert "Доступна" in get_batch_status(b1)
    assert get_batch_status(b2) == "Израсходована"


def test_batch_create_and_find(sample_preserve: Preserve) -> None:
    """Проверка функций create_batch, find_batch_by_id и consume."""
    batches: list[Batch] = []
    created = create_batch(batches, sample_preserve, "2026-09-20", 12)
    assert created is not None
    assert created.id == 1
    assert len(batches) == 1

    invalid = create_batch(batches, sample_preserve, "2026-09-20", -5)
    assert invalid is None

    found = find_batch_by_id(batches, 1)
    assert found is created

    assert consume_from_batch(batches, 1, 2) is True
    assert found.quantity == 10
    assert consume_from_batch(batches, 999, 1) is False
