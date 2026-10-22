"""Представления приложения batches."""

from datetime import date
from pathlib import Path
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from models.batches import Batch, get_active_batches
from storage import load_batches, load_preserves, load_products

DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
PRODUCTS_PATH = str(DATA_DIR / 'products.json')
PRESERVES_PATH = str(DATA_DIR / 'preserves.json')
BATCHES_PATH = str(DATA_DIR / 'batches.json')


def _load_all_batches() -> list[Batch]:
    products = load_products(PRODUCTS_PATH)
    preserves = load_preserves(PRESERVES_PATH, products)
    return load_batches(BATCHES_PATH, preserves)


def _batch_to_dict(batch: Batch) -> dict[str, Any]:
    try:
        parsed_date: Any = date.fromisoformat(batch.production_date)
    except (ValueError, TypeError):
        parsed_date = batch.production_date

    return {
        'id': batch.id,
        'preserve': batch.preserve,
        'preserve_name': batch.preserve.name,
        'preserve_id': batch.preserve.id,
        'product_name': batch.preserve.product.name,
        'production_date': parsed_date,
        'quantity': batch.quantity,
        'is_consumed': batch.is_consumed,
    }


def batch_list(request: HttpRequest) -> HttpResponse:
    """Отображение списка активных партий в погребе."""
    batches = _load_all_batches()
    active = get_active_batches(batches)
    context = {
        'batches': [_batch_to_dict(b) for b in active],
    }
    return render(request, 'batches/list.html', context)


def batch_detail(request: HttpRequest, batch_id: int) -> HttpResponse:
    """Детальная карточка конкретной партии."""
    batches = _load_all_batches()
    batch = next((b for b in batches if b.id == batch_id), None)

    if batch is None:
        return render(
            request,
            '404.html',
            {'message': f'Партия с идентификатором #{batch_id} не найдена.'},
            status=404,
        )

    return render(
        request,
        'batches/detail.html',
        {'batch': _batch_to_dict(batch)},
    )


def batch_search(request: HttpRequest) -> HttpResponse:
    """Поиск партий по дате выработки или статусу доступности."""
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

    context = {
        'batches': [_batch_to_dict(b) for b in filtered],
        'date_filter': date_filter,
        'status_filter': status_filter,
    }
    return render(request, 'batches/search.html', context)


def batch_statistics(request: HttpRequest) -> HttpResponse:
    """Агрегированная аналитическая статистика по запасам."""
    batches = _load_all_batches()
    active_batches = [b for b in batches if not b.is_consumed]
    total_jars = sum(b.quantity for b in active_batches)

    # Статистика по видам заготовок
    preserve_counter: dict[str, dict[str, Any]] = {}
    for b in batches:
        name = b.preserve.name
        if name not in preserve_counter:
            preserve_counter[name] = {
                'preserve_name': name,
                'batches_count': 0,
                'total_quantity': 0,
            }
        preserve_counter[name]['batches_count'] += 1
        preserve_counter[name]['total_quantity'] += b.quantity

    context = {
        'total_jars': total_jars,
        'active_batches_count': len(active_batches),
        'total_batches_count': len(batches),
        'preserve_stats': list(preserve_counter.values()),
    }
    return render(request, 'batches/statistics.html', context)
