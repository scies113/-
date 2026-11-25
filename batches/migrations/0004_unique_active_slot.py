from django.db import migrations, models


def check_active_slots(apps, schema_editor):
    Batch = apps.get_model("batches", "Batch")
    duplicates = (
        Batch.objects.using(schema_editor.connection.alias)
        .filter(status="active")
        .values("preserve_id", "production_date")
        .annotate(active_count=models.Count("pk"))
        .filter(active_count__gt=1)
    )
    if duplicates.exists():
        raise RuntimeError(
            "Найдены активные партии одной заготовки на одну дату. "
            "Разрешите конфликты в базе ПР10 перед переходом на ПР11."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("batches", "0003_batch_status"),
        ("preserves", "0003_preserve_slug"),
    ]

    operations = [
        migrations.RunPython(check_active_slots, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="batch",
            constraint=models.UniqueConstraint(
                condition=models.Q(status="active"),
                fields=("preserve", "production_date"),
                name="unique_active_batch_per_recipe_date",
                violation_error_message=(
                    "У этой заготовки уже есть активная партия на эту дату."
                ),
            ),
        ),
    ]
