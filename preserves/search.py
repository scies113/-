"""Поиск без учёта регистра, в том числе для русского текста в SQLite."""

from django.db.models import CharField, Func, Q


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


def search_names(queryset, term, *fields):
    """Ищет подстроку в одном или нескольких текстовых полях."""
    aliases = {
        f"search_text_{i}": Casefold(field) for i, field in enumerate(fields)
    }
    condition = Q()
    for alias in aliases:
        condition |= Q(**{f"{alias}__contains": term.casefold()})
    return queryset.alias(**aliases).filter(condition)
