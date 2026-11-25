"""Формы фильтрации партий."""

from django import forms

from preserves.models import Preserve, Product

from .models import Batch


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
