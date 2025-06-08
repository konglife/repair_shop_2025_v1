from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from repairs.utils.cost_calculation import calculate_historical_weighted_average_cost

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from .models import RepairJob, UsedPart


def calculate_repair_total(repair_job: RepairJob) -> Decimal:
    """Return total amount for a repair job."""
    labor = repair_job.labor_charge or Decimal('0.00')
    parts = repair_job.parts_cost_total or Decimal('0.00')
    return labor + parts


def assign_used_part_cost(used_part: UsedPart) -> None:
    """Assign cost price per unit and total cost for a used part."""
    cost_per_unit = calculate_historical_weighted_average_cost(used_part.product)
    used_part.cost_price_per_unit = cost_per_unit
    total_cost = cost_per_unit * used_part.quantity
    # Attribute exists? assign anyway
    if hasattr(used_part, 'total_cost'):
        used_part.total_cost = total_cost
    else:
        # assign attribute for runtime use
        used_part.total_cost = total_cost
