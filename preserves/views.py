"""Представления приложения preserves."""

from pathlib import Path

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound

from storage import load_preserves, load_products

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
PRODUCTS_PATH = str(DATA_DIR / 'products.json')
PRESERVES_PATH = str(DATA_DIR / 'preserves.json')


def preserve_list(request: HttpRequest) -> HttpResponse:
    """Отображение списка видов заготовок."""
    products = load_products(PRODUCTS_PATH)
    preserves = load_preserves(PRESERVES_PATH, products)

    items = "".join(
        f"<li><a href='/preserves/{p.id}/'>{p.name}</a> "
        f"(Основной продукт: {p.product.name})</li>"
        for p in preserves
    )
    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        "<title>Каталог заготовок</title></head>"
        "<body>"
        "<h1>Каталог заготовок</h1>"
        f"<ul>{items}</ul>"
        "<p><a href='/'>На главную</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)


def preserve_detail(request: HttpRequest, preserve_id: int) -> HttpResponse:
    """Карточка конкретной заготовки с описанием и сырьем."""
    products = load_products(PRODUCTS_PATH)
    preserves = load_preserves(PRESERVES_PATH, products)
    preserve = next((p for p in preserves if p.id == preserve_id), None)

    if preserve is None:
        return HttpResponseNotFound("<h1>404 — Заготовка не найдена</h1>")

    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        f"<title>{preserve.name}</title></head>"
        "<body>"
        f"<h1>Заготовка: {preserve.name}</h1>"
        f"<p><strong>Основной продукт:</strong> {preserve.product.name} "
        f"({preserve.product.category})</p>"
        f"<p><strong>Заметки к рецепту:</strong> "
        f"{preserve.recipe_notes or 'Нет данных'}</p>"
        "<p><a href='/preserves/'>Назад к списку</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)


def product_list(request: HttpRequest) -> HttpResponse:
    """Справочник базового сырья."""
    products = load_products(PRODUCTS_PATH)
    items = "".join(
        f"<li>[#{p.id}] {p.name} — категория: {p.category}</li>"
        for p in products
    )
    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        "<title>Справочник сырья</title></head>"
        "<body>"
        "<h1>Справочник сырья</h1>"
        f"<ul>{items}</ul>"
        "<p><a href='/'>На главную</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)
