"""Вспомогательные функции для валидации и безопасного ввода данных."""

from datetime import datetime


def input_int(
    prompt: str,
    min_val: int | None = None,
    max_val: int | None = None,
) -> int:
    """Запрашивает целое число с проверкой диапазона.

    :param prompt: Текст приглашения ко вводу.
    :param min_val: Минимально допустимое значение (включительно).
    :param max_val: Максимально допустимое значение (включительно).
    :return: Корректно введенное целое число.
    """
    while True:
        raw_val = input(prompt).strip()
        try:
            val = int(raw_val)
        except ValueError:
            print("Ошибка: введите корректное целое число.")
            continue

        if min_val is not None and val < min_val:
            print(f"Ошибка: число не может быть меньше {min_val}.")
            continue
        if max_val is not None and val > max_val:
            print(f"Ошибка: число не может быть больше {max_val}.")
            continue
        return val


def input_date(prompt: str) -> str:
    """Запрашивает дату в формате ГГГГ-ММ-ДД с проверкой корректности.

    :param prompt: Текст приглашения ко вводу.
    :return: Корректная строка даты в формате YYYY-MM-DD.
    """
    while True:
        raw_val = input(prompt).strip()
        try:
            parsed = datetime.strptime(raw_val, "%Y-%m-%d")
            return parsed.strftime("%Y-%m-%d")
        except ValueError:
            print("Ошибка: неверный формат даты. Используйте ГГГГ-ММ-ДД.")


def input_str(prompt: str, min_len: int = 1) -> str:
    """Запрашивает непустую строку с минимальной длиной.

    :param prompt: Текст приглашения ко вводу.
    :param min_len: Минимальная длина строки после удаления концевых пробелов.
    :return: Корректно введенная строка.
    """
    while True:
        val = input(prompt).strip()
        if len(val) >= min_len:
            return val
        print(f"Ошибка: строка должна содержать не менее {min_len} символов.")
