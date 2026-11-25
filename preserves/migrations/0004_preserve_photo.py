from django.db import migrations, models

import preserves.models


class Migration(migrations.Migration):
    dependencies = [
        ("preserves", "0003_preserve_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="preserve",
            name="photo",
            field=models.ImageField(
                blank=True,
                help_text=(
                    "JPEG, PNG или WebP до 5 МБ "
                    "и не более 4096 × 4096 пикселей."
                ),
                upload_to=preserves.models.preserve_photo_path,
                verbose_name="Фотография",
            ),
        ),
    ]
