"""Пакет объектно-ориентированной модели предметной области."""

from .batches import Batch
from .preserves import Preserve
from .products import Product

__all__ = ["Product", "Preserve", "Batch"]
