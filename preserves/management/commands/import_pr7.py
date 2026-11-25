"""Перенос данных из базы ПР7 в базу, созданную миграциями Django."""

from contextlib import closing
from datetime import date
from pathlib import Path
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction

from batches.models import Batch
from preserves.models import Preserve, Product


class Command(BaseCommand):
    help = "Копирует продукты, заготовки и партии из базы SQLite ПР7."
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            type=Path,
            default=settings.BASE_DIR / "data" / "preserves.sqlite",
            help="Путь к исходной базе ПР7.",
        )

    def handle(self, *args, **options):
        source = Path(options["source"]).resolve()
        if not source.is_file():
            raise CommandError(f"Исходный файл не найден: {source}")
        target = Path(settings.DATABASES["default"]["NAME"]).resolve()
        if source == target:
            raise CommandError("Исходный файл совпадает с базой Django.")

        try:
            with closing(sqlite3.connect(
                f"{source.as_uri()}?mode=ro", uri=True
            )) as legacy, transaction.atomic():
                legacy.row_factory = sqlite3.Row
                legacy.execute("BEGIN")
                counts = (
                    self.copy_rows(
                        legacy.execute(
                            "SELECT id, name, category FROM products"
                        ), Product
                    ),
                    self.copy_rows(
                        legacy.execute(
                            "SELECT id, name, product_id, recipe_notes "
                            "FROM preserves"
                        ), Preserve
                    ),
                    self.copy_rows(
                        legacy.execute(
                            "SELECT id, preserve_id, production_date, "
                            "quantity, is_consumed FROM batches"
                        ), Batch
                    ),
                )
        except (sqlite3.Error, DatabaseError, ValueError) as error:
            raise CommandError(f"Перенос отменён: {error}") from error

        for model, (total, created) in zip((Product, Preserve, Batch), counts):
            self.stdout.write(
                f"{model.__name__}: всего {total}, добавлено {created}"
            )

    @staticmethod
    def copy_rows(rows, model):
        total = created_count = 0
        for row in rows:
            fields = dict(row)
            pk = fields.pop("id")
            if model is Batch:
                fields["production_date"] = date.fromisoformat(
                    fields["production_date"]
                )
                status = fields.pop("is_consumed")
                if status not in (0, 1):
                    raise ValueError(f"Недопустимый статус партии #{pk}")
                fields["status"] = (
                    Batch.Status.CONSUMED if status else Batch.Status.ACTIVE
                )

            obj, created = model.objects.get_or_create(pk=pk, defaults=fields)
            if not created and any(
                getattr(obj, name) != value for name, value in fields.items()
            ):
                raise CommandError(
                    f"{model.__name__} #{pk} уже существует "
                    "с другими данными. Перенос отменён."
                )
            total += 1
            created_count += created
        return total, created_count
