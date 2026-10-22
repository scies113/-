"""Представления приложения preserves."""

from pathlib import Path

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from storage import load_preserves, load_products

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
PRODUCTS_PATH = str(DATA_DIR / 'products.json')
PRESERVES_PATH = str(DATA_DIR / 'preserves.json')


def preserve_list(request: HttpRequest) -> HttpResponse:
    """Отображение списка видов заготовок."""
    products = load_products(PRODUCTS_PATH)
    preserves = load_preserves(PRESERVES_PATH, products)
    return render(
        request,
        'preserves/list.html',
        {'preserves': preserves},
    )


def preserve_detail(request: HttpRequest, preserve_id: int) -> HttpResponse:
    """Карточка конкретной заготовки с описанием и сырьем."""
    products = load_products(PRODUCTS_PATH)
    preserves = load_preserves(PRESERVES_PATH, products)
    preserve = next((p for p in preserves if p.id == preserve_id), None)

    if preserve is None:
        return render(
            request,
            '404.html',
            {
                'message': (
                    f'Заготовка с идентификатором #{preserve_id} не найдена.'
                )
            },
            status=404,
        )

    return render(
        request,
        'preserves/detail.html',
        {'preserve': preserve},
    )


def product_list(request: HttpRequest) -> HttpResponse:
    """Справочник базового сырья."""
    products = load_products(PRODUCTS_PATH)
    return render(
        request,
        'preserves/products.html',
        {'products': products},
    )
