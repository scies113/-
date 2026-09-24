"""Система учета домашних заготовок (Прототип ПР1).

Модуль реализует базовый консольный функционал учета партий заготовок,
расчета остатков банок и контроля расхода домашней консервации.
"""


def get_batch_status(quantity: int, is_consumed: bool) -> str:
    """Возвращает строковый статус доступности партии банок.

    :param quantity: Текущий остаток банок в партии.
    :param is_consumed: Признак полного расхода партии.
    :return: Текстовое описание статуса.
    """
    if is_consumed or quantity <= 0:
        return "Израсходована"
    return f"Доступна для употребления ({quantity} шт.)"


def consume_batch(batch: dict, amount: int) -> bool:
    """Выполняет списание банок из партии.

    :param batch: Словарь с данными партии.
    :param amount: Количество банок для списания.
    :return: True при успешном списании, иначе False.
    """
    if amount <= 0:
        print("Ошибка: количество для списания должно быть больше нуля.")
        return False
    if amount > batch["quantity"]:
        print(f"Ошибка: недостаточно банок (в наличии: {batch['quantity']}).")
        return False

    batch["quantity"] -= amount
    if batch["quantity"] == 0:
        batch["is_consumed"] = True
    print(f"Успешно списано {amount} шт. Остаток: {batch['quantity']} шт.")
    return True


def show_batches(batches: list[dict]) -> None:
    """Выводит список партий в консоль.

    :param batches: Список словарей с партиями.
    """
    if not batches:
        print("Список партий пуст.")
        return

    print("\n--- Список партий заготовок ---")
    for batch in batches:
        status = get_batch_status(batch["quantity"], batch["is_consumed"])
        print(
            f"Партия #{batch['id']}: '{batch['preserve_name']}' "
            f"от {batch['production_date']} | "
            f"Количество: {batch['quantity']} шт. | Статус: {status}"
        )


def main() -> None:
    """Точка входа функционального прототипа ПР1."""
    products = [
        {"id": 1, "name": "Огурцы", "category": "овощи"},
        {"id": 2, "name": "Клубника", "category": "ягоды"},
    ]
    preserves = [
        {"id": 1, "name": "Маринованные огурцы", "product_name": "Огурцы"},
        {"id": 2, "name": "Клубничное варенье", "product_name": "Клубника"},
    ]
    batches = [
        {
            "id": 1,
            "preserve_name": "Маринованные огурцы",
            "production_date": "2026-09-10",
            "quantity": 10,
            "is_consumed": False,
        },
        {
            "id": 2,
            "preserve_name": "Клубничное варенье",
            "production_date": "2026-09-12",
            "quantity": 5,
            "is_consumed": False,
        },
    ]

    print("=== Система учета домашних заготовок (ПР1) ===")
    print(f"Загружено продуктов: {len(products)}, рецептов: {len(preserves)}")

    while True:
        print("\n1. Показать список партий")
        print("2. Списать банки из партии")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_batches(batches)
        elif choice == "2":
            show_batches(batches)
            batch_id_str = input("Введите номер партии: ").strip()
            amount_str = input("Введите количество для списания: ").strip()
            if not batch_id_str.isdigit() or not amount_str.isdigit():
                print("Ошибка: необходимо вводить целые числа.")
                continue
            batch_id = int(batch_id_str)
            amount = int(amount_str)
            target = next((b for b in batches if b["id"] == batch_id), None)
            if target:
                consume_batch(target, amount)
            else:
                print("Партия с указанным номером не найдена.")
        elif choice == "0":
            print("Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню. Повторите ввод.")


if __name__ == "__main__":
    main()
