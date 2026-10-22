"""Представления приложения preserves."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def preserve_list(request: HttpRequest) -> HttpResponse:
    """Отображение списка видов заготовок из базы данных SQLite."""
    sql = (
        "SELECT "
        "  p.id, "
        "  p.name, "
        "  p.recipe_notes, "
        "  pr.name AS product_name, "
        "  pr.category AS product_category "
        "FROM preserves p "
        "JOIN products pr ON p.product_id = pr.id "
        "ORDER BY p.name ASC;"
    )
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()

    return render(
        request,
        "preserves/list.html",
        {"preserves": rows},
    )


def preserve_detail(request: HttpRequest, preserve_id: int) -> HttpResponse:
    """Карточка конкретной заготовки с описанием и сырьем из SQLite."""
    sql = (
        "SELECT "
        "  p.id, "
        "  p.name, "
        "  p.recipe_notes, "
        "  pr.name AS product_name, "
        "  pr.category AS product_category "
        "FROM preserves p "
        "JOIN products pr ON p.product_id = pr.id "
        "WHERE p.id = ?;"
    )
    with get_connection() as conn:
        preserve = conn.execute(sql, [preserve_id]).fetchone()

    if preserve is None:
        return render(
            request,
            "404.html",
            {
                "message": (
                    f"Заготовка с идентификатором #{preserve_id} не найдена."
                )
            },
            status=404,
        )

    return render(
        request,
        "preserves/detail.html",
        {"preserve": preserve},
    )


def product_list(request: HttpRequest) -> HttpResponse:
    """Справочник базового сырья из SQLite."""
    sql = (
        "SELECT "
        "  pr.id, "
        "  pr.name, "
        "  pr.category, "
        "  COUNT(p.id) AS recipes_count "
        "FROM products pr "
        "LEFT JOIN preserves p ON pr.id = p.product_id "
        "GROUP BY pr.id, pr.name, pr.category "
        "ORDER BY pr.name ASC;"
    )
    with get_connection() as conn:
        products = conn.execute(sql).fetchall()

    return render(
        request,
        "preserves/products.html",
        {"products": products},
    )
