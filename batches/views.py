"""Представления приложения batches."""

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from preserves.models import Preserve, Product
from config.query_params import parse_iso_date

from .models import Batch


PAGE_SIZE = 5
SORT_OPTIONS = {
    "newest": ("Сначала новые", ("-production_date", "-pk")),
    "oldest": ("Сначала старые", ("production_date", "pk")),
    "quantity": (
        "По остатку банок", ("-available_quantity", "-production_date", "-pk")
    ),
    "preserve": (
        "По заготовке", ("preserve__name", "-production_date", "-pk")
    ),
}


def batch_list(request: HttpRequest) -> HttpResponse:
    """Постраничный список активных партий."""
    active = Batch.objects.active().select_related("preserve").order_by(
        "-production_date", "-pk"
    )
    page_obj = Paginator(active, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "batches/list.html", {"page_obj": page_obj})


def batch_detail(request: HttpRequest, batch_id: int) -> HttpResponse:
    """Карточка партии с заготовкой и сырьём в одном запросе."""
    try:
        batch = Batch.objects.with_details().get(pk=batch_id)
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
    preserve = request.GET.get("preserve", "").strip()
    product = request.GET.get("product", "").strip()
    sort = request.GET.get("sort", "newest")
    if sort not in SORT_OPTIONS:
        sort = "newest"

    product_rows = list(
        Product.objects.order_by("name", "pk").values_list(
            "pk", "name", "category"
        )
    )
    categories = sorted({name for _, _, name in product_rows})
    products = {str(pk): name for pk, name, _ in product_rows}
    preserves = {
        str(pk): name for pk, name in Preserve.objects.order_by(
            "name", "pk"
        ).values_list("pk", "name")
    }
    filters = {}
    errors = []
    if date_filter:
        try:
            filters["production_date"] = parse_iso_date(date_filter)
        except ValueError:
            errors.append("Введите дату в формате ГГГГ-ММ-ДД.")
    if status in Batch.Status.values:
        filters["status"] = status
    elif status:
        errors.append("Выберите допустимый статус.")
    if category in categories:
        filters["preserve__product__category"] = category
    elif category:
        errors.append("Выберите категорию из списка.")
    for value, options, field, message in (
        (preserve, preserves, "preserve_id", "Выберите заготовку из списка."),
        (
            product, products, "preserve__product_id",
            "Выберите сырьё из списка.",
        ),
    ):
        if value in options:
            filters[field] = int(value)
        elif value:
            errors.append(message)

    batches = Batch.objects.filter(**filters)
    if query:
        batches = batches.search(query)
    if errors:
        batches = batches.none()
    rows = batches.order_by(*SORT_OPTIONS[sort][1]).values(
        "id", "production_date", "status", "available_quantity",
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
        "statuses": Batch.Status.choices,
        "preserve_filter": preserve,
        "product_filter": product,
        "preserves": preserves,
        "products": products,
        "sort": sort,
        "sort_options": SORT_OPTIONS,
        "errors": errors,
    }
    return render(request, "batches/search.html", context)


def batch_statistics(request: HttpRequest) -> HttpResponse:
    """Сводка остатков и группировка партий по заготовкам."""
    summary = Batch.objects.aggregate(
        total_batches_count=Count("pk"),
        active_batches_count=Count("pk", filter=Q(status=Batch.Status.ACTIVE)),
        consumed_batches_count=Count(
            "pk", filter=Q(status=Batch.Status.CONSUMED)
        ),
        discarded_batches_count=Count(
            "pk", filter=Q(status=Batch.Status.DISCARDED)
        ),
        total_jars=Sum("available_quantity", default=0),
    )
    preserve_stats = Preserve.objects.annotate(
        batches_count=Count("batches"),
        total_quantity=Sum("batches__available_quantity", default=0),
    ).order_by("-total_quantity", "name", "pk")
    return render(
        request,
        "batches/statistics.html",
        {**summary, "preserve_stats": preserve_stats},
    )
