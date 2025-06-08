from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .models import Purchase


def calculate_purchase_total(purchase: "Purchase") -> Decimal:
    """Calculate total price for a ``Purchase`` instance.

    Parameters
    ----------
    purchase : Purchase
        The purchase to calculate the total price for.

    Returns
    -------
    Decimal
        ``quantity`` multiplied by ``price`` of the purchase.
    """

    return purchase.quantity * purchase.price


@transaction.atomic
def update_stock_after_purchase(purchase: "Purchase") -> None:
    """Update stock levels based on a completed ``Purchase``.

    Parameters
    ----------
    purchase : Purchase
        The purchase that was saved.

    Returns
    -------
    None
    """

    if purchase.status != "RECEIVED":
        return

    from django.apps import apps

    Stock = apps.get_model("inventory", "Stock")
    stock, created = Stock.objects.get_or_create(product=purchase.product)
    if created:
        stock.min_stock = 0
        stock.current_stock = purchase.quantity
        stock.average_cost = purchase.price or Decimal("0.00")
    else:
        total_cost = (
            stock.current_stock * stock.average_cost
        ) + (purchase.quantity * (purchase.price or Decimal("0.00")))
        stock.current_stock += purchase.quantity
        total_qty = stock.current_stock
        stock.average_cost = (total_cost / total_qty) if total_qty > 0 else Decimal("0.00")

    stock.last_updated_at = timezone.now()
    stock.save()

