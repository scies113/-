"""Представления приложения batches."""

from pathlib import Path

from django.http import HttpRequest, HttpResponse, HttpResponseNotFound

from models.batches import get_active_batches
from storage import load_batches, load_preserves, load_products

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
PRODUCTS_PATH = str(DATA_DIR / 'products.json')
PRESERVES_PATH = str(DATA_DIR / 'preserves.json')
BATCHES_PATH = str(DATA_DIR / 'batches.json')


def _load_all_batches():
    products = load_products(PRODUCTS_PATH)
    preserves = load_preserves(PRESERVES_PATH, products)
    batches = load_batches(BATCHES_PATH, preserves)
    return batches


def batch_list(request: HttpRequest) -> HttpResponse:
    """Отображение списка активных партий."""
    batches = _load_all_batches()
    active = get_active_batches(batches)

    items = "".join(
        f"<li><a href='/batches/{b.id}/'>Партия #{b.id}</a>: "
        f"{b.preserve.name} ({b.production_date}) — "
        f"{b.quantity} шт.</li>"
        for b in active
    )
    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        "<title>Партии в погребе</title></head>"
        "<body>"
        "<h1>Активные партии в погребе</h1>"
        f"<ul>{items}</ul>"
        "<p><a href='/'>На главную</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)


def batch_detail(request: HttpRequest, batch_id: int) -> HttpResponse:
    """Детальная информация о конкретной партии."""
    batches = _load_all_batches()
    batch = next((b for b in batches if b.id == batch_id), None)

    if batch is None:
        return HttpResponseNotFound("<h1>404 — Партия не найдена</h1>")

    status_str = "Израсходована" if batch.is_consumed else "Активна"
    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        f"<title>Партия #{batch.id}</title></head>"
        "<body>"
        f"<h1>Партия #{batch.id}: {batch.preserve.name}</h1>"
        f"<p><strong>Дата выработки:</strong> {batch.production_date}</p>"
        f"<p><strong>Количество банок:</strong> {batch.quantity} шт.</p>"
        f"<p><strong>Статус:</strong> {status_str}</p>"
        f"<p><strong>Сырье:</strong> {batch.preserve.product.name}</p>"
        "<p><a href='/batches/'>Назад к списку партий</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)


def batch_search(request: HttpRequest) -> HttpResponse:
    """Поиск партий по дате или статусу."""
    batches = _load_all_batches()
    date_filter = request.GET.get('date', '').strip()
    status_filter = request.GET.get('status', '').strip()

    filtered = batches
    if date_filter:
        filtered = [b for b in filtered if b.production_date == date_filter]
    if status_filter == 'active':
        filtered = [b for b in filtered if not b.is_consumed]
    elif status_filter == 'consumed':
        filtered = [b for b in filtered if b.is_consumed]

    items = "".join(
        f"<li><a href='/batches/{b.id}/'>Партия #{b.id}</a>: "
        f"{b.preserve.name} ({b.production_date}) — "
        f"{b.quantity} шт. "
        f"({'Израсходована' if b.is_consumed else 'Активна'})</li>"
        for b in filtered
    )
    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        "<title>Поиск партий</title></head>"
        "<body>"
        "<h1>Поиск партий</h1>"
        "<form method='get'>"
        "<label>Дата (ГГГГ-ММ-ДД): <input type='text' name='date' "
        f"value='{date_filter}'></label><br>"
        "<label>Статус: "
        "<select name='status'>"
        "<option value=''>Все</option>"
        "<option value='active'>Активные</option>"
        "<option value='consumed'>Израсходованные</option>"
        "</select></label><br>"
        "<button type='submit'>Найти</button>"
        "</form>"
        f"<h2>Результаты ({len(filtered)}):</h2>"
        f"<ul>{items}</ul>"
        "<p><a href='/'>На главную</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)


def batch_statistics(request: HttpRequest) -> HttpResponse:
    """Агрегированная статистика по запасам."""
    batches = _load_all_batches()
    total_batches = len(batches)
    active_batches = [b for b in batches if not b.is_consumed]
    total_jars = sum(b.quantity for b in active_batches)

    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        "<title>Статистика запасов</title></head>"
        "<body>"
        "<h1>Статистика запасов в погребе</h1>"
        f"<p>Всего партий: {total_batches}</p>"
        f"<p>Активных партий: {len(active_batches)}</p>"
        f"<p>Всего банок в наличии: {total_jars} шт.</p>"
        "<p><a href='/'>На главную</a></p>"
        "</body></html>"
    )
    return HttpResponse(content)
