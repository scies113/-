"""Представления приложения batches."""

from datetime import date
import sqlite3
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import get_connection


def _format_batch_row(row: sqlite3.Row) -> dict[str, Any]:
    """Преобразует строку БД в словарь с поддержкой форматирования дат."""
    item = dict(row)
    raw_date = item.get("production_date")
    if isinstance(raw_date, str):
        try:
            item["production_date"] = date.fromisoformat(raw_date)
        except (ValueError, TypeError):
            pass
    return item


def batch_list(request: HttpRequest) -> HttpResponse:
    """Отображение списка активных партий в погребе из базы данных."""
    sql = (
        "SELECT "
        "  b.id, "
        "  b.preserve_id, "
        "  p.name AS preserve_name, "
        "  b.production_date, "
        "  b.quantity, "
        "  b.is_consumed "
        "FROM batches b "
        "JOIN preserves p ON b.preserve_id = p.id "
        "WHERE b.is_consumed = 0 "
        "ORDER BY b.production_date DESC;"
    )
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()

    formatted = [_format_batch_row(r) for r in rows]
    return render(
        request,
        "batches/list.html",
        {"batches": formatted},
    )


def batch_detail(request: HttpRequest, batch_id: int) -> HttpResponse:
    """Детальная карточка конкретной партии с данными заготовки и сырья."""
    sql = (
        "SELECT "
        "  b.id, "
        "  b.preserve_id, "
        "  b.production_date, "
        "  b.quantity, "
        "  b.is_consumed, "
        "  p.name AS preserve_name, "
        "  p.recipe_notes, "
        "  pr.name AS product_name, "
        "  pr.category AS product_category "
        "FROM batches b "
        "JOIN preserves p ON b.preserve_id = p.id "
        "JOIN products pr ON p.product_id = pr.id "
        "WHERE b.id = ?;"
    )
    with get_connection() as conn:
        row = conn.execute(sql, [batch_id]).fetchone()

    if row is None:
        return render(
            request,
            "404.html",
            {
                "message": (
                    f"Партия с идентификатором #{batch_id} не найдена."
                )
            },
            status=404,
        )

    return render(
        request,
        "batches/detail.html",
        {"batch": _format_batch_row(row)},
    )


def batch_search(request: HttpRequest) -> HttpResponse:
    """Поиск партий по дате выработки или статусу доступности через SQL."""
    date_filter = request.GET.get("date", "").strip()
    status_filter = request.GET.get("status", "").strip()

    sql = (
        "SELECT "
        "  b.id, "
        "  b.preserve_id, "
        "  p.name AS preserve_name, "
        "  b.production_date, "
        "  b.quantity, "
        "  b.is_consumed "
        "FROM batches b "
        "JOIN preserves p ON b.preserve_id = p.id "
    )
    conditions = []
    params: list[Any] = []

    if date_filter:
        conditions.append("b.production_date = ?")
        params.append(date_filter)

    if status_filter == "active":
        conditions.append("b.is_consumed = 0")
    elif status_filter == "consumed":
        conditions.append("b.is_consumed = 1")

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY b.production_date DESC;"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()

    formatted = [_format_batch_row(r) for r in rows]
    context = {
        "batches": formatted,
        "date_filter": date_filter,
        "status_filter": status_filter,
    }
    return render(request, "batches/search.html", context)


def batch_statistics(request: HttpRequest) -> HttpResponse:
    """Агрегированная аналитическая статистика по запасам через SQL."""
    summary_sql = (
        "SELECT "
        "  COUNT(id) AS total_batches_count, "
        "  SUM(CASE WHEN is_consumed = 0 THEN 1 ELSE 0 END) "
        "    AS active_batches_count, "
        "  COALESCE("
        "    SUM(CASE WHEN is_consumed = 0 THEN quantity ELSE 0 END), 0"
        "  ) AS total_jars "
        "FROM batches;"
    )

    group_sql = (
        "SELECT "
        "  p.name AS preserve_name, "
        "  COUNT(b.id) AS batches_count, "
        "  COALESCE("
        "    SUM(CASE WHEN b.is_consumed = 0 THEN b.quantity ELSE 0 END), 0"
        "  ) AS total_quantity "
        "FROM preserves p "
        "LEFT JOIN batches b ON p.id = b.preserve_id "
        "GROUP BY p.id, p.name "
        "ORDER BY total_quantity DESC, p.name ASC;"
    )

    with get_connection() as conn:
        summary_row = conn.execute(summary_sql).fetchone()
        group_rows = conn.execute(group_sql).fetchall()

    total_jars = summary_row["total_jars"] if summary_row else 0
    active_count = summary_row["active_batches_count"] if summary_row else 0
    total_count = summary_row["total_batches_count"] if summary_row else 0

    preserve_stats = [
        {
            "preserve_name": r["preserve_name"],
            "batches_count": r["batches_count"],
            "total_quantity": r["total_quantity"],
        }
        for r in group_rows
    ]

    context = {
        "total_jars": total_jars,
        "active_batches_count": active_count,
        "total_batches_count": total_count,
        "preserve_stats": preserve_stats,
    }
    return render(request, "batches/statistics.html", context)
