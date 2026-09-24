"""Модуль описания сущности базового сырья/продукта."""

from typing import Any


class Product:
    """Описывает исходный продукт (сырье) для заготовок.

    :param product_id: Уникальный идентификатор продукта.
    :param name: Наименование продукта.
    :param category: Категория продукта (овощи, фрукты, ягоды и др.).
    """

    def __init__(self, product_id: int, name: str, category: str) -> None:
        """Инициализирует экземпляр продукта."""
        if not self.validate_name(name):
            raise ValueError(
                f"Некорректное наименование продукта: '{name}'. "
                "Длина должна быть не менее 2 символов."
            )
        self.id: int = product_id
        self.name: str = name.strip()
        self.category: str = category.strip()

    def __str__(self) -> str:
        """Возвращает строковое представление продукта."""
        return f"[#{self.id}] {self.name} (Категория: {self.category})"

    @staticmethod
    def validate_name(name: str) -> bool:
        """Проверяет валидность наименования продукта.

        :param name: Проверяемая строка названия.
        :return: True, если строка непустая и содержит от 2 символов.
        """
        return isinstance(name, str) and len(name.strip()) >= 2

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "Product":
        """Фабричный метод создания объекта из словаря данных.

        :param data: Словарь с полями id, name, category.
        :return: Экземпляр класса Product.
        """
        return cls(
            product_id=int(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
        )

    def to_dict(self) -> dict[str, Any]:
        """Преобразует объект продукта в словарь для сохранения.

        :return: Словарь с атрибутами продукта.
        """
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
        }


def add_product(
    products: list[Product],
    name: str,
    category: str,
) -> Product:
    """Создает новый продукт и добавляет его в общую коллекцию.

    :param products: Список существующих продуктов.
    :param name: Наименование продукта.
    :param category: Категория продукта.
    :return: Созданный экземпляр Product.
    """
    next_id = max([p.id for p in products], default=0) + 1
    new_product = Product(product_id=next_id, name=name, category=category)
    products.append(new_product)
    return new_product


def find_product_by_id(
    products: list[Product],
    product_id: int,
) -> Product | None:
    """Ищет продукт по его уникальному идентификатору.

    :param products: Список продуктов для поиска.
    :param product_id: Искомый ID.
    :return: Найденный экземпляр Product или None.
    """
    return next((p for p in products if p.id == product_id), None)


def find_products_by_name(
    products: list[Product],
    query: str,
) -> list[Product]:
    """Выполняет регистронезависимый поиск продуктов по подстроке.

    :param products: Список продуктов.
    :param query: Поисковый запрос.
    :return: Список подходящих продуктов.
    """
    cleaned_query = query.strip().lower()
    return [p for p in products if cleaned_query in p.name.lower()]


def show_products(products: list[Product]) -> None:
    """Отображает список продуктов в форматированном виде.

    :param products: Список продуктов для вывода.
    """
    if not products:
        print("Список продуктов пуст.")
        return

    print("\n--- Список доступных продуктов/сырья ---")
    for product in products:
        print(product)
