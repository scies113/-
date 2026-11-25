"""Модель партии домашних заготовок."""

from django.db import models


class Batch(models.Model):
    """Партия банок, приготовленных в одну дату по одному рецепту."""

    preserve = models.ForeignKey(
        "preserves.Preserve",
        on_delete=models.RESTRICT,
        related_name="batches",
        verbose_name="Заготовка",
    )
    production_date = models.DateField("Дата производства")
    quantity = models.PositiveIntegerField("Количество банок")
    is_consumed = models.BooleanField("Израсходована", default=False)

    class Meta:
        verbose_name = "партия"
        verbose_name_plural = "партии"

    def __str__(self):
        if self.pk is None:
            return "Новая партия"
        return f"Партия №{self.pk} от {self.production_date:%d.%m.%Y}"
