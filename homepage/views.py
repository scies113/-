"""Представления приложения homepage."""

from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from batches.models import Batch
from preserves.models import Preserve, Product


def index(request: HttpRequest) -> HttpResponse:
    """Главная страница с количеством рецептов, сырья и банок."""
    context = {
        "preserves_count": Preserve.objects.count(),
        "products_count": Product.objects.count(),
        "total_jars": Batch.objects.aggregate(
            total=Sum("available_quantity", default=0)
        )["total"],
        "largest_batches": Batch.objects.available()
        .select_related("preserve").order_by("-quantity", "-pk")[:3],
    }
    return render(request, "homepage/index.html", context)
