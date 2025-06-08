from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from inventory.models import Product, Stock

from repairs.utils.cost_calculation import calculate_historical_weighted_average_cost

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .models import RepairJob, UsedPart


def calculate_repair_total(repair_job: RepairJob) -> Decimal:
    """Return total amount for a repair job."""
    labor = repair_job.labor_charge or Decimal('0.00')
    parts = repair_job.parts_cost_total or Decimal('0.00')
    return labor + parts


def reduce_stock(product: Product, quantity: int) -> None:
    """Subtract ``quantity`` from the stock for ``product``.

    Raises:
        ValueError: If stock would become negative or the stock record does not exist.
    """
    try:
        stock = Stock.objects.select_for_update().get(product=product)
    except Stock.DoesNotExist as exc:
        raise ValueError("Stock record does not exist") from exc

    if stock.current_stock - quantity < 0:
        raise ValueError("Insufficient stock")

    stock.current_stock -= quantity
    stock.save()


def assign_used_part_cost(used_part: UsedPart) -> None:
    """Assign cost details to ``used_part`` and reduce inventory stock."""
    with transaction.atomic():
        cost_per_unit = calculate_historical_weighted_average_cost(used_part.product)
        used_part.cost_price_per_unit = cost_per_unit
        total_cost = cost_per_unit * used_part.quantity
        used_part.total_cost = total_cost
        reduce_stock(used_part.product, used_part.quantity)
