"""Поиск без учёта регистра, в том числе для русского текста в SQLite."""

from django.db.models import CharField, Func


def register_casefold(sender, connection, **kwargs):
    if connection.vendor == "sqlite":
        connection.connection.create_function(
            "CASEFOLD", 1, str.casefold, deterministic=True
        )


class Casefold(Func):
    """SQLite LOWER обрабатывает только ASCII без расширения ICU."""

    function = "CASEFOLD"
    output_field = CharField()

    def as_sql(self, compiler, connection, **extra_context):
        if connection.vendor != "sqlite":
            extra_context["function"] = "LOWER"
        return super().as_sql(compiler, connection, **extra_context)
