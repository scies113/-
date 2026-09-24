"""Система учета домашних заготовок (Модульная структура ПР2).

Точка входа, координация работы с хранилищем и модулем ввода.
"""

from pathlib import Path

from storage import load_json_data, save_json_data
from utils import input_int

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BATCHES_FILE = str(DATA_DIR / "batches.json")


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
            f"Партия #{batch['id']} от {batch['production_date']} | "
            f"Количество: {batch['quantity']} шт. | Статус: {status}"
        )


def main() -> None:
    """Точка входа модульного приложения ПР2."""
    batches = load_json_data(BATCHES_FILE)
    print("=== Система учета домашних заготовок (ПР2) ===")
    print(f"Загружено партий из хранилища: {len(batches)}")

    while True:
        print("\n1. Показать список партий в погребе")
        print("2. Списать банки из партии")
        print("9. Сохранить изменения")
        print("0. Выход")
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_batches(batches)
        elif choice == "2":
            show_batches(batches)
            batch_id = input_int("Введите номер партии: ", min_val=1)
            amount = input_int(
                "Введите количество для списания: ",
                min_val=1,
            )
            target = next((b for b in batches if b["id"] == batch_id), None)
            if target:
                consume_batch(target, amount)
            else:
                print("Партия с указанным номером не найдена.")
        elif choice == "9":
            save_json_data(BATCHES_FILE, batches)
            print("Данные успешно сохранены.")
        elif choice == "0":
            save_json_data(BATCHES_FILE, batches)
            print("Изменения сохранены. Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню. Повторите ввод.")


if __name__ == "__main__":
    main()
