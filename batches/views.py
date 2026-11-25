"""Представления приложения batches."""

from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, F, Q, Sum
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from preserves.models import Preserve

from .forms import BatchFilterForm, BatchForm, SORT_OPTIONS
from .models import ACTIVE_BATCH_CONFLICT, Batch


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


def _batch_form(request, batch=None):
    form = BatchForm(
        request.POST if request.method == "POST" else None, instance=batch
    )
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                if batch is None:
                    batch = form.save()
                else:
                    pending = form.save(commit=False)
                    updated = Batch.objects.active().filter(pk=batch.pk)
                    if not updated.update(
                        preserve=pending.preserve,
                        production_date=pending.production_date,
                        quantity=pending.quantity,
                    ):
                        raise Http404("Активная партия не найдена.")
        except IntegrityError:
            if not form.active_slot_taken():
                raise
            form.add_error(None, ACTIVE_BATCH_CONFLICT)
        else:
            return redirect("batches:detail", batch_id=batch.pk)

    return render(request, "edit_form.html", {
        "form": form,
        "title": "Редактирование партии" if batch else "Новая партия",
        "back_url": (
            reverse("batches:detail", args=[batch.pk])
            if batch else reverse("batches:list")
        ),
    })


@require_http_methods(["GET", "POST"])
@login_required
@permission_required("batches.add_batch", raise_exception=True)
def batch_create(request):
    return _batch_form(request)


@require_http_methods(["GET", "POST"])
@login_required
@permission_required("batches.change_batch", raise_exception=True)
def batch_update(request, batch_id):
    batch = get_object_or_404(Batch.objects.active(), pk=batch_id)
    return _batch_form(request, batch)


@require_POST
@login_required
@permission_required("batches.change_batch", raise_exception=True)
def batch_discard(request, batch_id):
    batch = get_object_or_404(Batch.objects.active(), pk=batch_id)
    if not batch.discard():
        raise Http404("Активная партия не найдена.")
    return redirect("batches:list")


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
