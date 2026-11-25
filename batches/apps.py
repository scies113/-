"""Конфигурация приложения batches."""

from django.apps import AppConfig


class BatchesConfig(AppConfig):
    """Класс конфигурации приложения batches."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'batches'
    verbose_name = 'Погреб'
