"""Тесты функций безопасного ввода и валидации (ПР2)."""

import pytest

from utils import input_date, input_int, input_str


def test_input_str_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверка ввода валидной непустой строки."""
    monkeypatch.setattr("builtins.input", lambda _: "  Огурцы  ")
    result = input_str("Продукт: ", min_len=2)
    assert result == "Огурцы"


def test_input_date_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверка ввода корректной даты."""
    monkeypatch.setattr("builtins.input", lambda _: "2026-09-15")
    result = input_date("Дата: ")
    assert result == "2026-09-15"


def test_input_int_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    """Проверка ввода корректного целого числа в диапазоне."""
    monkeypatch.setattr("builtins.input", lambda _: "10")
    result = input_int("Число: ", min_val=1, max_val=20)
    assert result == 10
