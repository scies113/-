"""Модель партии домашних заготовок."""

from django.db import models
from django.db.models import Case, F, Q, Value, When

from preserves.search import search_names


ACTIVE_BATCH_CONFLICT = (
    "У этой заготовки уже есть активная партия на эту дату."
)


class BatchStatus(models.TextChoices):
    ACTIVE = "active", "В наличии"
    CONSUMED = "consumed", "Израсходована"
    DISCARDED = "discarded", "Списана"


class BatchQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=BatchStatus.ACTIVE)

    def available(self):
        return self.active().filter(quantity__gt=0)

    def with_details(self):
        return self.select_related("preserve__product")

    def search(self, term):
        return search_names(
            self, term, "preserve__name", "preserve__product__name"
        )


class Batch(models.Model):
    """Партия банок, приготовленных в одну дату по одному рецепту."""

    Status = BatchStatus
    objects = BatchQuerySet.as_manager()

    preserve = models.ForeignKey(
        "preserves.Preserve",
        on_delete=models.RESTRICT,
        related_name="batches",
        verbose_name="Заготовка",
    )
    production_date = models.DateField("Дата производства")
    quantity = models.PositiveIntegerField("Количество банок")
    status = models.CharField(
        "Статус", max_length=10, choices=Status.choices,
        default=Status.ACTIVE,
    )
    available_quantity = models.GeneratedField(
        verbose_name="Банок в наличии",
        expression=Case(
            When(status=Status.ACTIVE, then=F("quantity")),
            default=Value(0),
        ),
        output_field=models.PositiveIntegerField(),
        db_persist=False,
    )

    class Meta:
        verbose_name = "партия"
        verbose_name_plural = "партии"
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=BatchStatus.values),
                name="batch_status_valid",
            ),
            models.UniqueConstraint(
                fields=("preserve", "production_date"),
                condition=Q(status=BatchStatus.ACTIVE),
                name="unique_active_batch_per_recipe_date",
                violation_error_message=ACTIVE_BATCH_CONFLICT,
            ),
        ]

    def discard(self):
        """Списывает активную партию и сохраняет её в истории."""
        updated = type(self).objects.active().filter(pk=self.pk).update(
            status=self.Status.DISCARDED
        )
        if updated:
            self.status = self.Status.DISCARDED
        return bool(updated)

    def __str__(self):
        if self.pk is None:
            return "Новая партия"
        return f"Партия №{self.pk} от {self.production_date:%d.%m.%Y}"
