"""Модуль описания сущности вида/рецепта заготовки."""

from typing import Any

from .products import Product


class Preserve:
    """Описывает вид или рецепт заготовки.

    Содержит ссылку на объект используемого сырья (Product).

    :param preserve_id: Уникальный идентификатор заготовки.
    :param name: Название заготовки (рецепта).
    :param product: Экземпляр Product, выступающий основным сырьем.
    :param recipe_notes: Заметки к рецепту или условия хранения.
    """

    def __init__(
        self,
        preserve_id: int,
        name: str,
        product: Product,
        recipe_notes: str = "",
    ) -> None:
        """Инициализирует экземпляр заготовки."""
        if not isinstance(product, Product):
            raise TypeError("Параметр product должен быть экземпляром Product")
        self.id: int = preserve_id
        self.name: str = name.strip()
        self.product: Product = product
        self.recipe_notes: str = recipe_notes.strip()

    def __str__(self) -> str:
        """Возвращает строковое представление заготовки."""
        return (
            f"[#{self.id}] Заготовка: '{self.name}' "
            f"(Основной продукт: {self.product.name})"
        )

    @classmethod
    def from_data(cls, data: dict[str, Any], product: Product) -> "Preserve":
        """Фабричный метод создания объекта из словаря данных.

        :param data: Словарь с данными заготовки.
        :param product: Связанный экземпляр Product.
        :return: Экземпляр класса Preserve.
        """
        return cls(
            preserve_id=int(data["id"]),
            name=str(data["name"]),
            product=product,
            recipe_notes=str(data.get("recipe_notes", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Сериализует объект заготовки в словарь с внешним ключом product_id.

        :return: Словарь с атрибутами заготовки.
        """
        return {
            "id": self.id,
            "name": self.name,
            "product_id": self.product.id,
            "recipe_notes": self.recipe_notes,
        }


def add_preserve(
    preserves: list[Preserve],
    name: str,
    product: Product,
    notes: str = "",
) -> Preserve:
    """Создает новую заготовку и добавляет ее в коллекцию.

    :param preserves: Список существующих заготовок.
    :param name: Название заготовки.
    :param product: Экземпляр базового продукта.
    :param notes: Примечания к рецепту.
    :return: Созданный экземпляр Preserve.
    """
    next_id = max([p.id for p in preserves], default=0) + 1
    new_preserve = Preserve(
        preserve_id=next_id,
        name=name,
        product=product,
        recipe_notes=notes,
    )
    preserves.append(new_preserve)
    return new_preserve


def find_preserve_by_id(
    preserves: list[Preserve],
    preserve_id: int,
) -> Preserve | None:
    """Ищет заготовку по её идентификатору.

    :param preserves: Список заготовок.
    :param preserve_id: Искомый ID.
    :return: Найденный экземпляр Preserve или None.
    """
    return next((p for p in preserves if p.id == preserve_id), None)


def filter_preserves_by_product(
    preserves: list[Preserve],
    product_id: int,
) -> list[Preserve]:
    """Фильтрует заготовки по идентификатору используемого сырья.

    :param preserves: Список заготовок.
    :param product_id: Идентификатор продукта.
    :return: Список отфильтрованных заготовок.
    """
    return [p for p in preserves if p.product.id == product_id]


def show_preserves(preserves: list[Preserve]) -> None:
    """Отображает список заготовок в форматированном виде.

    :param preserves: Список заготовок для отображения.
    """
    if not preserves:
        print("Список заготовок пуст.")
        return

    print("\n--- Список рецептов / заготовок ---")
    for preserve in preserves:
        notes_info = (
            f" [Заметки: {preserve.recipe_notes}]"
            if preserve.recipe_notes
            else ""
        )
        print(f"{preserve}{notes_info}")
