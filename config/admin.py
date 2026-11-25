"""Общие настройки административных списков."""

from django.contrib import admin

from preserves.search import search_names


class PreserveProjectAdmin(admin.ModelAdmin):
    list_per_page = 20

    def get_search_results(self, request, queryset, search_term):
        term = search_term.strip()
        if term:
            queryset = search_names(queryset, term, *self.search_fields)
        return queryset, False
