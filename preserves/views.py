"""Представления приложения preserves."""

from django.db.models import Count, Exists, OuterRef
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from batches.models import Batch
from config.query_params import parse_iso_date

from .models import Preserve, Product
from .search import search_names


def preserve_list(request: HttpRequest) -> HttpResponse:
    """Каталог с поиском и проверкой запасов на дату производства."""
    query = request.GET.get("q", "").strip()
    date_filter = request.GET.get("date", "").strip()
    date_error = ""
    preserves = Preserve.objects.select_related("product").order_by("name")
    if query:
        preserves = search_names(preserves, query, "name")
    if date_filter:
        try:
            production_date = parse_iso_date(date_filter)
        except ValueError:
            date_error = "Введите дату в формате ГГГГ-ММ-ДД."
            preserves = preserves.none()
        else:
            stock = Batch.objects.available().filter(
                preserve_id=OuterRef("pk"), production_date=production_date
            )
            preserves = preserves.filter(Exists(stock))

    return render(
        request,
        "preserves/list.html",
        {
            "preserves": preserves,
            "query": query,
            "date_filter": date_filter,
            "date_error": date_error,
        },
    )


def preserve_detail(
    request: HttpRequest,
    preserve_id: int | None = None,
    slug: str | None = None,
) -> HttpResponse:
    """Карточка заготовки по слагу или по прежнему числовому адресу."""
    lookup = {"slug": slug} if slug is not None else {"pk": preserve_id}
    label = slug if slug is not None else f"№{preserve_id}"
    try:
        preserve = get_object_or_404(
            Preserve.objects.select_related("product"), **lookup
        )
    except Http404:
        return render(
            request,
            "404.html",
            {"message": f"Заготовка «{label}» не найдена."},
            status=404,
        )

    return render(request, "preserves/detail.html", {"preserve": preserve})


def product_list(request: HttpRequest) -> HttpResponse:
    """Справочник сырья, включая продукты без рецептов."""
    products = Product.objects.annotate(
        recipes_count=Count("preserves")
    ).order_by("name")
    return render(request, "preserves/products.html", {"products": products})
