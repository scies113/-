"""Представления приложения homepage."""

from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница системы учета домашних заготовок."""
    content = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'>"
        "<title>Главная — Система учета домашних заготовок</title></head>"
        "<body>"
        "<h1>Система учета домашних заготовок</h1>"
        "<p>Добро пожаловать в веб-приложение для учета домашних заготовок, "
        "сырья и партий в погребе.</p>"
        "<ul>"
        "<li><a href='/preserves/'>Каталог заготовок</a></li>"
        "<li><a href='/preserves/products/'>Справочник сырья</a></li>"
        "<li><a href='/batches/'>Партии в погребе</a></li>"
        "<li><a href='/batches/search/'>Поиск партий</a></li>"
        "<li><a href='/batches/statistics/'>Статистика запасов</a></li>"
        "</ul>"
        "</body></html>"
    )
    return HttpResponse(content)
