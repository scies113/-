"""Главный модуль приложения «Система учета домашних заготовок».

Организует интерактивное консольное меню, координирует пользовательские
сценарии, загрузку и сохранение коллекций объектов.
"""

from pathlib import Path

from models.batches import (
    Batch,
    create_batch,
    find_batch_by_id,
    get_active_batches,
    show_batches,
    sort_batches_by_date,
)
from models.preserves import (
    Preserve,
    add_preserve,
    find_preserve_by_id,
    show_preserves,
)
from models.products import (
    Product,
    add_product,
    find_product_by_id,
    show_products,
)
from storage import (
    load_batches,
    load_preserves,
    load_products,
    save_batches,
    save_preserves,
    save_products,
)
from utils import input_date, input_int, input_str

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
PRODUCTS_FILE = str(DATA_DIR / "products.json")
PRESERVES_FILE = str(DATA_DIR / "preserves.json")
BATCHES_FILE = str(DATA_DIR / "batches.json")


def save_all_data(
    products: list[Product],
    preserves: list[Preserve],
    batches: list[Batch],
) -> None:
    """Сохраняет все коллекции в соответствующие JSON-файлы.

    :param products: Список продуктов.
    :param preserves: Список заготовок.
    :param batches: Список партий.
    """
    save_products(PRODUCTS_FILE, products)
    save_preserves(PRESERVES_FILE, preserves)
    save_batches(BATCHES_FILE, batches)


def handle_show_preserves_and_products(
    products: list[Product],
    preserves: list[Preserve],
) -> None:
    """Отображает список продуктов и рецептов заготовок."""
    show_products(products)
    show_preserves(preserves)


def handle_add_product(products: list[Product]) -> None:
    """Сценарий добавления нового исходного продукта."""
    print("\n--- Добавление нового сырья/продукта ---")
    name = input_str(
        "Введите наименование продукта (от 2 символов): ",
        min_len=2,
    )
    category = input_str(
        "Введите категорию (овощи, фрукты, ягоды, грибы и др.): ",
        min_len=2,
    )
    product = add_product(products, name, category)
    print(f"Успешно добавлен: {product}")


def handle_add_preserve(
    preserves: list[Preserve],
    products: list[Product],
) -> None:
    """Сценарий добавления нового рецепта/вида заготовки."""
    print("\n--- Добавление нового рецепта заготовки ---")
    if not products:
        print("Ошибка: сначала добавьте хотя бы один исходный продукт!")
        return

    show_products(products)
    prod_id = input_int("Введите ID базового продукта: ", min_val=1)
    product = find_product_by_id(products, prod_id)
    if product is None:
        print(f"Ошибка: продукт с ID #{prod_id} не найден.")
        return

    name = input_str(
        "Введите название заготовки (например, 'Маринованные огурцы'): ",
        min_len=2,
    )
    notes = input(
        "Введите примечания к рецепту (или Enter, чтобы пропустить): "
    ).strip()
    preserve = add_preserve(preserves, name, product, notes)
    print(f"Успешно добавлена заготовка: {preserve}")


def handle_create_batch(
    batches: list[Batch],
    preserves: list[Preserve],
) -> None:
    """Сценарий регистрации изготовленной партии заготовок."""
    print("\n--- Регистрация изготовленной партии ---")
    if not preserves:
        print("Ошибка: сначала добавьте хотя бы один рецепт заготовки!")
        return

    show_preserves(preserves)
    pres_id = input_int("Введите ID заготовки/рецепта: ", min_val=1)
    preserve = find_preserve_by_id(preserves, pres_id)
    if preserve is None:
        print(f"Ошибка: заготовка с ID #{pres_id} не найдена.")
        return

    prod_date = input_date("Введите дату изготовления (ГГГГ-ММ-ДД): ")
    quantity = input_int(
        "Введите количество изготовленных банок: ",
        min_val=1,
    )
    batch = create_batch(batches, preserve, prod_date, quantity)
    if batch:
        print(f"Партия успешно создана: {batch}")
    else:
        print("Ошибка при создании партии.")


def handle_consume_batch(batches: list[Batch]) -> None:
    """Сценарий списания банок из партии."""
    print("\n--- Списание банок из партии ---")
    active_batches = get_active_batches(batches)
    if not active_batches:
        print("Нет активных партий с доступными банками.")
        return

    show_batches(active_batches)
    batch_id = input_int("Введите ID партии для списания: ", min_val=1)
    batch = find_batch_by_id(batches, batch_id)
    if batch is None:
        print(f"Ошибка: партия с ID #{batch_id} не найдена.")
        return

    if batch.is_consumed:
        print("Ошибка: выбранная партия уже полностью израсходована.")
        return

    amount = input_int(
        f"Сколько банок списать (в наличии: {batch.quantity})? ",
        min_val=1,
        max_val=batch.quantity,
    )
    if batch.consume(amount):
        print(
            f"Списано {amount} шт. "
            f"Остаток в партии #{batch.id}: {batch.quantity} шт."
        )
        if batch.is_consumed:
            print(f"Внимание: партия #{batch.id} полностью израсходована!")
    else:
        print("Ошибка: не удалось выполнить списание.")


def handle_search_preserves(preserves: list[Preserve]) -> None:
    """Сценарий поиска заготовок по названию."""
    print("\n--- Поиск заготовок по названию ---")
    query = input_str("Введите название или часть названия для поиска: ")
    query_lower = query.lower()
    matched = [p for p in preserves if query_lower in p.name.lower()]
    if not matched:
        print(f"Заготовок по запросу '{query}' не найдено.")
    else:
        print(f"Найдено заготовок: {len(matched)}")
        for pres in matched:
            print(pres)


def handle_sort_batches(batches: list[Batch]) -> None:
    """Сценарий сортировки партий по дате изготовления."""
    print("\n--- Сортировка партий по дате изготовления ---")
    if not batches:
        print("Список партий пуст.")
        return

    print("1. Сначала самые свежие (по убыванию даты)")
    print("2. Сначала самые ранние (по возрастанию даты)")
    order = input("Выберите порядок сортировки (по умолчанию 1): ").strip()
    reverse = order != "2"
    sorted_list = sort_batches_by_date(batches, reverse=reverse)
    show_batches(sorted_list)


def main() -> None:
    """Точка входа интерактивного консольного приложения."""
    products = load_products(PRODUCTS_FILE)
    preserves = load_preserves(PRESERVES_FILE, products)
    batches = load_batches(BATCHES_FILE, preserves)

    print("=" * 45)
    print("  Система учета домашних заготовок (ПР3)")
    print("=" * 45)
    print(
        f"Загружено: продуктов - {len(products)}, "
        f"рецептов - {len(preserves)}, партий - {len(batches)}"
    )

    while True:
        print("\n=== Система учета домашних заготовок ===")
        print("1. Показать список партий в погребе")
        print("2. Показать виды заготовок и продукты")
        print("3. Добавить новый исходный продукт")
        print("4. Добавить рецепт/вид заготовки")
        print("5. Зарегистрировать изготовленную партию (дата, количество)")
        print("6. Списать/израсходовать банки из партии")
        print("7. Поиск заготовок по названию")
        print("8. Сортировка партий по дате изготовления")
        print("9. Сохранить изменения")
        print("0. Выход из программы")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_batches(batches)
        elif choice == "2":
            handle_show_preserves_and_products(products, preserves)
        elif choice == "3":
            handle_add_product(products)
        elif choice == "4":
            handle_add_preserve(preserves, products)
        elif choice == "5":
            handle_create_batch(batches, preserves)
        elif choice == "6":
            handle_consume_batch(batches)
        elif choice == "7":
            handle_search_preserves(preserves)
        elif choice == "8":
            handle_sort_batches(batches)
        elif choice == "9":
            save_all_data(products, preserves, batches)
            print("Все изменения успешно сохранены.")
        elif choice == "0":
            save_all_data(products, preserves, batches)
            print("Данные успешно сохранены. Завершение работы программы.")
            break
        else:
            print("Неверный пункт меню. Пожалуйста, повторите ввод.")


if __name__ == "__main__":
    main()
