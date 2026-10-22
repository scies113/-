"""Корневая маршрутизация проекта home_preserves."""

from typing import Any

from django.http import HttpRequest, HttpResponseNotFound
from django.urls import include, path


def custom_page_not_found(
    request: HttpRequest,
    exception: Any = None,
) -> HttpResponseNotFound:
    """Глобальный обработчик ошибки 404."""
    content = "<h1>404 — Страница не найдена</h1>"
    return HttpResponseNotFound(content)


handler404 = 'config.urls.custom_page_not_found'

urlpatterns = [
    path('', include('homepage.urls')),
    path('preserves/', include('preserves.urls')),
    path('batches/', include('batches.urls')),
]
