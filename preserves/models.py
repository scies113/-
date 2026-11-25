"""Модели справочника сырья и рецептов."""

from django.db import models


class Product(models.Model):
    """Сырьё для домашних заготовок."""

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Preserve(models.Model):
    """Вид домашней заготовки и её рецепт."""

    name = models.CharField(max_length=200)
    product = models.ForeignKey(
        Product, on_delete=models.RESTRICT, related_name="preserves"
    )
    recipe_notes = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name
