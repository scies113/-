"""Формы фильтрации партий."""

from django import forms
from django.utils import timezone

from preserves.models import Preserve, Product

from .models import ACTIVE_BATCH_CONFLICT, Batch


SORT_OPTIONS = {
    "newest": ("Сначала новые", ("-production_date", "-pk")),
    "oldest": ("Сначала старые", ("production_date", "pk")),
    "quantity": (
        "По остатку банок", ("-available_quantity", "-production_date", "-pk")
    ),
    "preserve": (
        "По заготовке", ("preserve__name", "-production_date", "-pk")
    ),
}


class BatchFilterForm(forms.Form):
    q = forms.CharField(
        label="Название заготовки или сырья", required=False, max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "type": "search"}
        ),
    )
    category = forms.ChoiceField(
        label="Категория сырья", required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    preserve = forms.TypedChoiceField(
        label="Заготовка", required=False, coerce=int, empty_value=None,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    product = forms.TypedChoiceField(
        label="Сырьё", required=False, coerce=int, empty_value=None,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date = forms.DateField(
        label="Дата производства", required=False,
        input_formats=("%Y-%m-%d",),
        help_text="Формат ГГГГ-ММ-ДД.",
        widget=forms.DateInput(attrs={"class": "form-control"}),
    )
    status = forms.ChoiceField(
        label="Статус партии", required=False,
        choices=[("", "Все статусы"), *Batch.Status.choices],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        label="Сортировка", required=False, initial="newest",
        choices=[
            (name, option[0]) for name, option in SORT_OPTIONS.items()
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        products = list(Product.objects.order_by("name", "pk").values_list(
            "pk", "name", "category"
        ))
        recipes = list(Preserve.objects.order_by("name", "pk").values_list(
            "pk", "name", "product_id"
        ))
        self.recipe_products = {pk: product for pk, _, product in recipes}
        self.fields["product"].choices = [
            ("", "Всё сырьё"), *((pk, name) for pk, name, _ in products)
        ]
        self.fields["preserve"].choices = [
            ("", "Все заготовки"), *((pk, name) for pk, name, _ in recipes)
        ]
        categories = sorted({name for _, _, name in products if name})
        self.fields["category"].choices = [
            ("", "Все категории"), *((name, name) for name in categories)
        ]

    def clean(self):
        cleaned = super().clean()
        preserve, product = cleaned.get("preserve"), cleaned.get("product")
        if preserve is not None and product is not None:
            if self.recipe_products[preserve] != product:
                raise forms.ValidationError(
                    "Выбранная заготовка относится к другому сырью."
                )
        return cleaned


class BatchForm(forms.ModelForm):
    production_date = forms.DateField(
        label="Дата производства",
        input_formats=("%Y-%m-%d",),
        initial=timezone.localdate,
        help_text="Для новой партии укажите сегодняшнюю или будущую дату.",
        widget=forms.DateInput(
            format="%Y-%m-%d",
            attrs={"class": "form-control", "type": "date"},
        ),
    )
    quantity = forms.IntegerField(
        label="Количество банок", min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Batch
        fields = ("preserve", "production_date", "quantity")
        widgets = {"preserve": forms.Select(attrs={"class": "form-select"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preserve"].queryset = Preserve.objects.order_by(
            "name", "pk"
        )

    def clean_production_date(self):
        value = self.cleaned_data["production_date"]
        same_slot = (
            self.instance.pk is not None
            and value == self.instance.production_date
            and "preserve" not in self.changed_data
        )
        if value < timezone.localdate() and not same_slot:
            raise forms.ValidationError(
                "Нельзя выбрать прошедшую дату для новой партии "
                "или переноса существующей."
            )
        return value

    def active_slot_taken(self):
        preserve = self.cleaned_data.get("preserve")
        day = self.cleaned_data.get("production_date")
        if preserve is None or day is None:
            return False
        return Batch.objects.active().filter(
            preserve=preserve, production_date=day
        ).exclude(pk=self.instance.pk).exists()

    def clean(self):
        cleaned = super().clean()
        if self.active_slot_taken():
            raise forms.ValidationError(ACTIVE_BATCH_CONFLICT)
        return cleaned
