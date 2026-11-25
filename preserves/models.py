"""Модели справочника сырья и рецептов."""

from uuid import uuid4

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


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
    slug = models.SlugField(
        "Слаг", max_length=220, allow_unicode=True, unique=True,
        help_text="Используется в адресе страницы заготовки.",
    )

    class Meta:
        verbose_name = "заготовка"
        verbose_name_plural = "заготовки"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)[:190] or "заготовка"
            suffix = self.pk if self.pk is not None else uuid4().hex[:12]
            self.slug = f"{base}-{suffix}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("preserves:detail_by_slug", kwargs={"slug": self.slug})
