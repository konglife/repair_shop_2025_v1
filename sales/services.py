"""Service functions for the ``sales`` app."""

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db import transaction

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .models import SaleItem


def calculate_sale_item_price(sale_item: "SaleItem") -> Decimal:
    """Return the selling price for a ``SaleItem``.

    Parameters
    ----------
    sale_item : SaleItem
        The sale item for which to determine the unit price.

    Returns
    -------
    Decimal
        The ``selling_price`` of the related product.
    """

    return sale_item.product.selling_price


@transaction.atomic
def update_stock_after_sale(sale_item: "SaleItem") -> None:
    """Decrement stock based on a saved ``SaleItem``.

    Parameters
    ----------
    sale_item : SaleItem
        The sale item that was saved.

    Returns
    -------
    None
    """

    stock = sale_item.product.stocks.first()
    if not stock:
        return

    quantity_difference = sale_item.quantity - getattr(sale_item, "_old_quantity", 0)
    stock.current_stock -= quantity_difference
    stock.save()

