"""Представления приложения batches."""

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from preserves.models import Preserve

from .forms import BatchFilterForm, SORT_OPTIONS
from .models import Batch


PAGE_SIZE = 5


def batch_list(request: HttpRequest) -> HttpResponse:
    """Постраничный список активных партий."""
    active = Batch.objects.active().select_related("preserve").order_by(
        "-production_date", "-pk"
    )
    page_obj = Paginator(active, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "batches/list.html", {"page_obj": page_obj})


def batch_detail(request: HttpRequest, batch_id: int) -> HttpResponse:
    """Карточка партии с заготовкой и сырьём в одном запросе."""
    try:
        batch = Batch.objects.with_details().get(pk=batch_id)
    except Batch.DoesNotExist:
        return render(
            request,
            "404.html",
            {"message": f"Партия с идентификатором #{batch_id} не найдена."},
            status=404,
        )

    return render(request, "batches/detail.html", {"batch": batch})


def batch_search(request: HttpRequest) -> HttpResponse:
    """Поиск по названию заготовки или сырья и совместные фильтры."""
    form = BatchFilterForm(request.GET or None)
    batches = Batch.objects.all()
    sort = "newest"
    if form.is_bound:
        if form.is_valid() or set(form.errors) == {"sort"}:
            data = form.cleaned_data
            sort = data.get("sort") or sort
            filters = {
                field: data[param]
                for field, param in (
                    ("production_date", "date"),
                    ("status", "status"),
                    ("preserve_id", "preserve"),
                    ("preserve__product_id", "product"),
                    ("preserve__product__category", "category"),
                )
                if data.get(param)
            }
            batches = batches.filter(**filters)
            if data["q"]:
                batches = batches.search(data["q"])
        else:
            batches = batches.none()
    rows = batches.order_by(*SORT_OPTIONS[sort][1]).values(
        "id", "production_date", "status", "available_quantity",
        preserve_name=F("preserve__name"),
    )
    page_obj = Paginator(rows, PAGE_SIZE).get_page(request.GET.get("page"))
    return render(request, "batches/search.html", {
        "page_obj": page_obj,
        "form": form,
    })


def batch_statistics(request: HttpRequest) -> HttpResponse:
    """Сводка остатков и группировка партий по заготовкам."""
    summary = Batch.objects.aggregate(
        total_batches_count=Count("pk"),
        active_batches_count=Count("pk", filter=Q(status=Batch.Status.ACTIVE)),
        consumed_batches_count=Count(
            "pk", filter=Q(status=Batch.Status.CONSUMED)
        ),
        discarded_batches_count=Count(
            "pk", filter=Q(status=Batch.Status.DISCARDED)
        ),
        total_jars=Sum("available_quantity", default=0),
    )
    preserve_stats = Preserve.objects.annotate(
        batches_count=Count("batches"),
        total_quantity=Sum("batches__available_quantity", default=0),
    ).order_by("-total_quantity", "name", "pk")
    return render(
        request,
        "batches/statistics.html",
        {**summary, "preserve_stats": preserve_stats},
    )
