"""Корневая маршрутизация проекта home_preserves."""

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import include, path


def custom_page_not_found(
    request: HttpRequest,
    exception: Any = None,
) -> HttpResponse:
    """Глобальный обработчик ошибки 404."""
    return render(
        request,
        '404.html',
        {'message': 'Запрашиваемая страница не существует.'},
        status=404,
    )


handler404 = 'config.urls.custom_page_not_found'

urlpatterns = [
    path('', include('homepage.urls')),
    path('preserves/', include('preserves.urls')),
    path('batches/', include('batches.urls')),
]
