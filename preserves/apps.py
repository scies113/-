"""Конфигурация приложения preserves."""

from django.apps import AppConfig


class PreservesConfig(AppConfig):
    """Класс конфигурации приложения preserves."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'preserves'

    def ready(self):
        from django.db.backends.signals import connection_created

        from .search import register_casefold

        connection_created.connect(register_casefold, dispatch_uid=__name__)
