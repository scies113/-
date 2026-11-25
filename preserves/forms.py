"""Форма заготовки с загрузкой фотографии."""

from pathlib import Path

from django import forms

from .models import Preserve


class PreservePhotoField(forms.ImageField):
    """Одинаковая проверка загрузок на сайте и в Django Admin."""

    allowed_formats = {
        "JPEG": {".jpg", ".jpeg"},
        "PNG": {".png"},
        "WEBP": {".webp"},
    }

    def to_python(self, data):
        if data and data.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Размер фотографии не должен превышать 5 МБ."
            )
        upload = super().to_python(data)
        if upload is None:
            return None

        image = upload.image
        extensions = self.allowed_formats.get(image.format, set())
        if Path(upload.name).suffix.lower() not in extensions:
            raise forms.ValidationError(
                "Загрузите JPEG, PNG или WebP с соответствующим расширением."
            )
        if max(image.size) > 4096:
            raise forms.ValidationError(
                "Ширина и высота фотографии не должны превышать 4096 пикселей."
            )
        return upload


class PreserveForm(forms.ModelForm):
    class Meta:
        model = Preserve
        fields = ("name", "product", "recipe_notes", "photo")
        field_classes = {"photo": PreservePhotoField}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "product": forms.Select(attrs={"class": "form-select"}),
            "recipe_notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
            "photo": forms.ClearableFileInput(attrs={
                "class": "form-control",
                "accept": "image/jpeg,image/png,image/webp",
            }),
        }
