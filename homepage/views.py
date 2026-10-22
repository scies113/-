"""Представления приложения homepage."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница системы учета домашних заготовок."""
    with get_connection() as conn:
        preserves_count = conn.execute(
            "SELECT COUNT(*) FROM preserves;"
        ).fetchone()[0]
        products_count = conn.execute(
            "SELECT COUNT(*) FROM products;"
        ).fetchone()[0]
        jars_row = conn.execute(
            "SELECT COALESCE(SUM(quantity), 0) FROM batches "
            "WHERE is_consumed = 0;"
        ).fetchone()
        total_jars = jars_row[0] if jars_row else 0

    context = {
        "preserves_count": preserves_count,
        "products_count": products_count,
        "total_jars": total_jars,
    }
    return render(request, "homepage/index.html", context)
