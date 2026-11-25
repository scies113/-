"""Модели справочника сырья и рецептов."""

from django.db import models


class Product(models.Model):
    """Сырьё для домашних заготовок."""

    name = models.CharField("Название", max_length=200)
    category = models.CharField("Категория", max_length=100)

    class Meta:
        verbose_name = "продукт"
        verbose_name_plural = "продукты"

    def __str__(self):
        return self.name


class Preserve(models.Model):
    """Вид домашней заготовки и её рецепт."""

    name = models.CharField("Название", max_length=200)
    product = models.ForeignKey(
        Product, on_delete=models.RESTRICT, related_name="preserves",
        verbose_name="Сырьё",
    )
    recipe_notes = models.TextField(
        "Примечания к рецепту", blank=True, default=""
    )

    class Meta:
        verbose_name = "заготовка"
        verbose_name_plural = "заготовки"

    def __str__(self):
        return self.name
