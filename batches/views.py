"""Представления приложения batches."""

from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from preserves.models import Preserve, Product
from preserves.search import Casefold

from .models import Batch


PAGE_SIZE = 5
SORT_OPTIONS = {
    "newest": ("Сначала новые", ("-production_date", "-pk")),
    "oldest": ("Сначала старые", ("production_date", "pk")),
    "quantity": ("По остатку банок", ("-quantity", "-production_date", "-pk")),
    "preserve": (
        "По заготовке", ("preserve__name", "-production_date", "-pk")
    ),
}


def batch_list(request: HttpRequest) -> HttpResponse:
    """Постраничный список активных партий."""
    active = Batch.objects.select_related("preserve").exclude(
        is_consumed=True
    ).order_by("-production_date", "-pk")
    page_obj = Paginator(active, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "batches/list.html", {"page_obj": page_obj})


def batch_detail(request: HttpRequest, batch_id: int) -> HttpResponse:
    """Карточка партии с заготовкой и сырьём в одном запросе."""
    try:
        batch = Batch.objects.select_related("preserve__product").get(
            pk=batch_id
        )
    except Batch.DoesNotExist:
        return render(
            request,
            "404.html",
            {"message": f"Партия с идентификатором #{batch_id} не найдена."},
            status=404,
        )

    return render(request, "batches/detail.html", {"batch": batch})


def batch_search(request: HttpRequest) -> HttpResponse:
    """Поиск по названию заготовки или сырья и совместные фильтры."""
    query = request.GET.get("q", "").strip()
    date_filter = request.GET.get("date", "").strip()
    status = request.GET.get("status", "").strip()
    category = request.GET.get("category", "").strip()
    sort = request.GET.get("sort", "newest")
    if sort not in SORT_OPTIONS:
        sort = "newest"

    categories = list(
        Product.objects.order_by("category").values_list(
            "category", flat=True
        ).distinct()
    )
    filters = {}
    errors = []
    if date_filter:
        try:
            production_date = date.fromisoformat(date_filter)
            if production_date.isoformat() != date_filter:
                raise ValueError
            filters["production_date"] = production_date
        except ValueError:
            errors.append("Введите дату в формате ГГГГ-ММ-ДД.")
    if status in {"active", "consumed"}:
        filters["is_consumed"] = status == "consumed"
    elif status:
        errors.append("Выберите допустимый статус.")
    if category in categories:
        filters["preserve__product__category"] = category
    elif category:
        errors.append("Выберите категорию из списка.")

    batches = Batch.objects.filter(**filters)
    if query:
        term = query.casefold()
        batches = batches.alias(
            preserve_search=Casefold("preserve__name"),
            product_search=Casefold("preserve__product__name"),
        ).filter(
            Q(preserve_search__contains=term)
            | Q(product_search__contains=term)
        )
    if errors:
        batches = batches.none()
    rows = batches.order_by(*SORT_OPTIONS[sort][1]).values(
        "id", "production_date", "quantity", "is_consumed",
        preserve_name=F("preserve__name"),
    )
    page_obj = Paginator(rows, PAGE_SIZE).get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "query": query,
        "date_filter": date_filter,
        "status_filter": status,
        "category_filter": category,
        "categories": categories,
        "sort": sort,
        "sort_options": SORT_OPTIONS,
        "errors": errors,
    }
    return render(request, "batches/search.html", context)


def batch_statistics(request: HttpRequest) -> HttpResponse:
    """Сводка остатков и группировка партий по заготовкам."""
    active = Q(is_consumed=False)
    summary = Batch.objects.aggregate(
        total_batches_count=Count("pk"),
        active_batches_count=Count("pk", filter=active),
        total_jars=Sum("quantity", filter=active, default=0),
    )
    preserve_stats = Preserve.objects.annotate(
        batches_count=Count("batches"),
        total_quantity=Sum(
            "batches__quantity",
            filter=Q(batches__is_consumed=False),
            default=0,
        ),
    ).order_by("-total_quantity", "name", "pk")
    return render(
        request,
        "batches/statistics.html",
        {**summary, "preserve_stats": preserve_stats},
    )
