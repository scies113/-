"""Модуль описания сущности изготовленной партии заготовок."""

from typing import Any

from .preserves import Preserve


class Batch:
    """Описывает конкретную изготовленную партию заготовок.

    :param batch_id: Уникальный идентификатор партии.
    :param preserve: Экземпляр Preserve, ссылка на рецепт/заготовку.
    :param production_date: Дата изготовления в формате ГГГГ-ММ-ДД.
    :param quantity: Количество банок в наличии.
    """

    def __init__(
        self,
        batch_id: int,
        preserve: Preserve,
        production_date: str,
        quantity: int,
    ) -> None:
        """Инициализирует экземпляр партии с валидацией остатка."""
        if not isinstance(preserve, Preserve):
            raise TypeError(
                "Параметр preserve должен быть экземпляром Preserve"
            )
        if not self.validate_quantity(quantity):
            raise ValueError(
                f"Некорректное количество банок: {quantity}. "
                "Ожидается неотрицательное целое число."
            )

        self.id: int = batch_id
        self.preserve: Preserve = preserve
        self.production_date: str = production_date.strip()
        self.quantity: int = quantity
        self.is_consumed: bool = quantity == 0

    def __str__(self) -> str:
        """Возвращает строковое представление партии."""
        status_label = "[ИЗРАСХОДОВАНА]" if self.is_consumed else "[АКТИВНА]"
        return (
            f"[Партия #{self.id}] '{self.preserve.name}' "
            f"от {self.production_date}: {self.quantity} шт. {status_label}"
        )

    def consume(self, amount: int) -> bool:
        """Бизнес-метод списания банок из партии.

        :param amount: Количество банок для списания.
        :return: True, если списание выполнено успешно; False при нехватке.
        """
        if amount <= 0 or amount > self.quantity:
            return False

        self.quantity -= amount
        if self.quantity == 0:
            self.is_consumed = True
        return True

    @staticmethod
    def validate_quantity(quantity: int) -> bool:
        """Проверяет корректность количества банок.

        :param quantity: Проверяемое значение.
        :return: True, если значение является неотрицательным целым числом.
        """
        return (
            isinstance(quantity, int)
            and not isinstance(quantity, bool)
            and quantity >= 0
        )

    @classmethod
    def from_data(cls, data: dict[str, Any], preserve: Preserve) -> "Batch":
        """Фабричный метод создания партии из словаря данных.

        :param data: Словарь с атрибутами партии.
        :param preserve: Экземпляр Preserve.
        :return: Экземпляр Batch.
        """
        batch = cls(
            batch_id=int(data["id"]),
            preserve=preserve,
            production_date=str(data["production_date"]),
            quantity=int(data["quantity"]),
        )
        if "is_consumed" in data:
            batch.is_consumed = bool(data["is_consumed"])
        return batch

    def to_dict(self) -> dict[str, Any]:
        """Сериализует объект партии в словарь для сохранения.

        :return: Словарь с атрибутами партии.
        """
        return {
            "id": self.id,
            "preserve_id": self.preserve.id,
            "production_date": self.production_date,
            "quantity": self.quantity,
            "is_consumed": self.is_consumed,
        }


def create_batch(
    batches: list[Batch],
    preserve: Preserve,
    prod_date: str,
    quantity: int,
) -> Batch | None:
    """Создает новую партию и регистрирует ее в коллекции.

    :param batches: Список существующих партий.
    :param preserve: Экземпляр заготовки.
    :param prod_date: Дата изготовления.
    :param quantity: Количество изготовленных банок.
    :return: Созданный экземпляр Batch или None при невалидном количестве.
    """
    if not Batch.validate_quantity(quantity):
        return None

    next_id = max([b.id for b in batches], default=0) + 1
    new_batch = Batch(
        batch_id=next_id,
        preserve=preserve,
        production_date=prod_date,
        quantity=quantity,
    )
    batches.append(new_batch)
    return new_batch


def find_batch_by_id(batches: list[Batch], batch_id: int) -> Batch | None:
    """Ищет партию по идентификатору.

    :param batches: Список партий.
    :param batch_id: Искомый ID.
    :return: Экземпляр Batch или None.
    """
    return next((b for b in batches if b.id == batch_id), None)


def consume_from_batch(
    batches: list[Batch],
    batch_id: int,
    amount: int,
) -> bool:
    """Списывает банки из партии по её идентификатору.

    :param batches: Список партий.
    :param batch_id: Идентификатор партии.
    :param amount: Количество для списания.
    :return: True при успешном списании, иначе False.
    """
    batch = find_batch_by_id(batches, batch_id)
    if not batch:
        return False
    return batch.consume(amount)


def get_active_batches(batches: list[Batch]) -> list[Batch]:
    """Возвращает список не израсходованных партий через генератор.

    :param batches: Список всех партий.
    :return: Список активных партий.
    """
    return [b for b in batches if not b.is_consumed]


def sort_batches_by_date(
    batches: list[Batch],
    reverse: bool = True,
) -> list[Batch]:
    """Сортирует партии по дате изготовления с lambda-функцией.

    :param batches: Список партий.
    :param reverse: Флаг обратного порядка (по умолчанию свежие первыми).
    :return: Новый отсортированный список партий.
    """
    return sorted(batches, key=lambda b: b.production_date, reverse=reverse)


def get_batch_status(batch: Batch) -> str:
    """Возвращает текстовый статус доступности партии для употребления.

    :param batch: Экземпляр партии.
    :return: Строковое описание статуса.
    """
    if batch.is_consumed or batch.quantity <= 0:
        return "Израсходована"
    return f"Доступна для употребления ({batch.quantity} шт.)"


def show_batches(batches: list[Batch]) -> None:
    """Отображает список партий в консоли.

    :param batches: Список партий для вывода.
    """
    if not batches:
        print("Список партий пуст.")
        return

    print("\n--- Список партий заготовок в погребе ---")
    for batch in batches:
        print(batch)
