"""Модель партии домашних заготовок."""

from django.db import models


class Batch(models.Model):
    """Партия банок, приготовленных в одну дату по одному рецепту."""

    preserve = models.ForeignKey(
        "preserves.Preserve", on_delete=models.RESTRICT, related_name="batches"
    )
    production_date = models.DateField()
    quantity = models.PositiveIntegerField()
    is_consumed = models.BooleanField(default=False)

    def __str__(self):
        return f"Партия #{self.pk} от {self.production_date:%d.%m.%Y}"
