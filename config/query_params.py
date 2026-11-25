"""Разбор дат из параметров пользовательского запроса."""

from datetime import date


def parse_iso_date(value):
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError("Ожидалась дата в формате ГГГГ-ММ-ДД.")
    return result
