from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Preserve = apps.get_model("preserves", "Preserve")
    rows = Preserve.objects.using(schema_editor.connection.alias)
    for pk, name in rows.values_list("pk", "name").iterator():
        base = slugify(name, allow_unicode=True)[:190] or "заготовка"
        rows.filter(pk=pk).update(slug=f"{base}-{pk}")


class Migration(migrations.Migration):
    dependencies = [
        ("preserves", "0002_localize_admin"),
    ]

    operations = [
        migrations.AddField(
            model_name="preserve",
            name="slug",
            field=models.SlugField(
                max_length=220, allow_unicode=True, null=True
            ),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="preserve",
            name="slug",
            field=models.SlugField(
                verbose_name="Слаг", max_length=220,
                allow_unicode=True, unique=True,
                help_text="Используется в адресе страницы заготовки.",
            ),
        ),
    ]
