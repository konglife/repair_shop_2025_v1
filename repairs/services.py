from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction

from inventory.models import Stock

if TYPE_CHECKING:
    from .models import RepairJob, UsedPart


# calculate_repair_total is no longer needed under the new logic, as total_amount is set by user and labor_charge is calculated as total_amount - parts_cost_total.
# This function has been removed.

def apply_used_part_cost(used_part: "UsedPart") -> Decimal:
    """Assign weighted-average cost from Stock to a used part and return its total cost.

    Parameters
    ----------
    used_part : UsedPart
        The used part instance that needs cost calculation.

    Returns
    -------
    Decimal
        The total cost for this part (cost per unit multiplied by quantity).
    """
    try:
        stock = Stock.objects.get(product=used_part.product)
        cost_per_unit = stock.average_cost
    except Stock.DoesNotExist:
        # If no stock record, default cost to 0. This case should be rare.
        cost_per_unit = Decimal('0.00')

    used_part.cost_price_per_unit = cost_per_unit
    return cost_per_unit * used_part.quantity
