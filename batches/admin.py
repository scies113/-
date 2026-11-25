"""Администрирование партий банок."""

from django.contrib import admin

from config.admin import PreserveProjectAdmin

from .models import Batch


@admin.register(Batch)
class BatchAdmin(PreserveProjectAdmin):
    list_display = (
        "id", "preserve", "product_name", "production_date", "quantity",
        "status", "available_quantity",
    )
    list_display_links = ("id", "preserve")
    list_filter = ("status", "production_date", "preserve__product")
    list_select_related = ("preserve__product",)
    search_fields = ("preserve__name", "preserve__product__name")
    ordering = ("-production_date", "-pk")
    autocomplete_fields = ("preserve",)
    date_hierarchy = "production_date"
    readonly_fields = ("available_jars",)

    @admin.display(description="Сырьё", ordering="preserve__product__name")
    def product_name(self, obj):
        return obj.preserve.product.name

    @admin.display(description="Банок в наличии")
    def available_jars(self, obj):
        return obj.available_quantity if obj and obj.pk is not None else None
