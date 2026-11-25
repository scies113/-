"""Администрирование продуктов и заготовок."""

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.models import BaseInlineFormSet

from batches.models import ACTIVE_BATCH_CONFLICT, Batch
from config.admin import PreserveProjectAdmin

from .forms import PreservePhotoField
from .models import Preserve, Product


class PreserveInline(admin.TabularInline):
    model = Preserve
    fields = ("name", "recipe_notes")
    extra = 0
    show_change_link = True


class BatchInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return
        active_dates = set()
        for form in self.forms:
            values = form.cleaned_data
            day = values.get("production_date")
            if values.get("DELETE") or (
                values.get("status") != Batch.Status.ACTIVE
            ):
                continue
            if day in active_dates:
                raise ValidationError(ACTIVE_BATCH_CONFLICT)
            active_dates.add(day)


class BatchInline(admin.TabularInline):
    model = Batch
    formset = BatchInlineFormSet
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
    formfield_overrides = {
        models.ImageField: {"form_class": PreservePhotoField},
    }
    list_display = ("name", "product")
    list_filter = ("product__category",)
    list_select_related = ("product",)
    search_fields = ("name", "product__name")
    ordering = ("name", "pk")
    autocomplete_fields = ("product",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (BatchInline,)
