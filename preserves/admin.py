"""Администрирование продуктов и заготовок."""

from django.contrib import admin

from batches.models import Batch
from config.admin import PreserveProjectAdmin

from .models import Preserve, Product


class PreserveInline(admin.TabularInline):
    model = Preserve
    fields = ("name", "recipe_notes")
    extra = 0
    show_change_link = True


class BatchInline(admin.TabularInline):
    model = Batch
    fields = ("production_date", "quantity", "status")
    ordering = ("-production_date", "-pk")
    extra = 0
    show_change_link = True


@admin.register(Product)
class ProductAdmin(PreserveProjectAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category")
    ordering = ("name", "pk")
    inlines = (PreserveInline,)


@admin.register(Preserve)
class PreserveAdmin(PreserveProjectAdmin):
    list_display = ("name", "product")
    list_filter = ("product__category",)
    list_select_related = ("product",)
    search_fields = ("name", "product__name")
    ordering = ("name", "pk")
    autocomplete_fields = ("product",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (BatchInline,)
