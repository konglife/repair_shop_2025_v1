from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction

from repairs.utils.cost_calculation import calculate_historical_weighted_average_cost

if TYPE_CHECKING:
    from .models import RepairJob, UsedPart


def calculate_repair_total(repair_job: "RepairJob") -> Decimal:
    """Calculate the total amount for a repair job.

    Parameters
    ----------
    repair_job : RepairJob
        The repair job instance for which to calculate the total.

    Returns
    -------
    Decimal
        Sum of ``labor_charge`` and ``parts_cost_total``.
    """
    return repair_job.labor_charge + repair_job.parts_cost_total


def apply_used_part_cost(used_part: "UsedPart") -> Decimal:
    """Assign weighted-average cost to a used part and return its total cost.

    Parameters
    ----------
    used_part : UsedPart
        The used part instance that needs cost calculation.

    Returns
    -------
    Decimal
        The total cost for this part (cost per unit multiplied by quantity).
    """
    cost_per_unit = calculate_historical_weighted_average_cost(used_part.product)
    used_part.cost_price_per_unit = cost_per_unit
    return cost_per_unit * used_part.quantity


def calculate_parts_cost(product, quantity=1):
    """Return Decimal: weighted-average cost per unit * quantity."""
    from .utils.cost_calculation import calculate_historical_weighted_average_cost
    unit_cost = calculate_historical_weighted_average_cost(product)
    return unit_cost * quantity


def compute_labor_from_total(total_amount, parts_cost):
    """Return Decimal: labor charge = total_amount - parts_cost."""
    return total_amount - parts_cost
