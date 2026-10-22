"""Представления приложения homepage."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница системы учета домашних заготовок."""
    return render(request, 'homepage/index.html')
