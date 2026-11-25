"""Представления приложения preserves."""

from django.db.models import Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Preserve, Product
from .search import Casefold


def preserve_list(request: HttpRequest) -> HttpResponse:
    """Каталог с поиском по названию заготовки."""
    query = request.GET.get("q", "").strip()
    preserves = Preserve.objects.select_related("product").order_by("name")
    if query:
        preserves = preserves.alias(search_name=Casefold("name")).filter(
            search_name__contains=query.casefold()
        )

    return render(
        request,
        "preserves/list.html",
        {"preserves": preserves, "query": query},
    )


def preserve_detail(request: HttpRequest, preserve_id: int) -> HttpResponse:
    """Карточка заготовки и связанного сырья."""
    try:
        preserve = Preserve.objects.select_related("product").get(
            pk=preserve_id
        )
    except Preserve.DoesNotExist:
        return render(
            request,
            "404.html",
            {"message": f"Заготовка с ID #{preserve_id} не найдена."},
            status=404,
        )

    return render(request, "preserves/detail.html", {"preserve": preserve})


def product_list(request: HttpRequest) -> HttpResponse:
    """Справочник сырья, включая продукты без рецептов."""
    products = Product.objects.annotate(
        recipes_count=Count("preserves")
    ).order_by("name")
    return render(request, "preserves/products.html", {"products": products})
