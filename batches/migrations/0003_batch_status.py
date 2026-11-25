from django.db import migrations, models


def convert_legacy_status(apps, schema_editor):
    Batch = apps.get_model("batches", "Batch")
    rows = Batch.objects.using(schema_editor.connection.alias)
    rows.filter(is_consumed=True).update(status="consumed")
    rows.filter(is_consumed=False).update(status="active")


def restore_legacy_status(apps, schema_editor):
    Batch = apps.get_model("batches", "Batch")
    rows = Batch.objects.using(schema_editor.connection.alias)
    rows.exclude(status="active").update(is_consumed=True)
    rows.filter(status="active").update(is_consumed=False)


class Migration(migrations.Migration):
    dependencies = [
        ("batches", "0002_localize_admin"),
    ]

    operations = [
        migrations.AddField(
            model_name="batch",
            name="status",
            field=models.CharField(
                verbose_name="Статус", max_length=10, default="active",
                choices=[
                    ("active", "В наличии"),
                    ("consumed", "Израсходована"),
                    ("discarded", "Списана"),
                ],
            ),
        ),
        migrations.RunPython(convert_legacy_status, restore_legacy_status),
        migrations.RemoveField(model_name="batch", name="is_consumed"),
        migrations.AddConstraint(
            model_name="batch",
            constraint=models.CheckConstraint(
                condition=models.Q(
                    status__in=["active", "consumed", "discarded"]
                ),
                name="batch_status_valid",
            ),
        ),
        migrations.AddField(
            model_name="batch",
            name="available_quantity",
            field=models.GeneratedField(
                verbose_name="Банок в наличии",
                expression=models.Case(
                    models.When(status="active", then=models.F("quantity")),
                    default=models.Value(0),
                ),
                output_field=models.PositiveIntegerField(),
                db_persist=False,
            ),
        ),
    ]
