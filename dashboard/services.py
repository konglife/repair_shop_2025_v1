from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Tuple

from django.db import transaction


def calculate_daily_summary(date: date) -> Tuple[Decimal, Decimal]:
    """Calculate total revenue and profit for a given day.

    Parameters
    ----------
    date : date
        The date of the summary being calculated.

    Returns
    -------
    Tuple[Decimal, Decimal]
        A tuple ``(total_revenue, total_profit)`` computed from the
        :class:`~dashboard.models.DailySummary` for that date. If no
        summary exists, both values will be ``Decimal('0')``.
    """
    from .models import DailySummary  # local import to avoid circular dependency

    summary = DailySummary.objects.filter(date=date).only(
        "total_sales_revenue",
        "total_repairs_revenue",
        "total_sales_profit",
        "total_repairs_profit",
    ).first()

    if not summary:
        return Decimal("0"), Decimal("0")

    total_revenue = summary.total_sales_revenue + summary.total_repairs_revenue
    total_profit = summary.total_sales_profit + summary.total_repairs_profit
    return total_revenue, total_profit


def calculate_monthly_summary(year: int, month: int) -> Tuple[Decimal, Decimal]:
    """Calculate total revenue and profit for a month.

    Parameters
    ----------
    year : int
        Year of the month to summarise.
    month : int
        Month number (1-12).

    Returns
    -------
    Tuple[Decimal, Decimal]
        A tuple ``(total_revenue, total_profit)`` computed from the
        :class:`~dashboard.models.MonthlySummary` identified by the
        provided ``year`` and ``month``. If no summary exists, ``Decimal('0')``
        is returned for both values.
    """
    from .models import MonthlySummary  # local import to avoid circular dependency

    month_str = f"{year:04d}-{month:02d}"
    summary = MonthlySummary.objects.filter(month=month_str).only(
        "total_sales_revenue",
        "total_repairs_revenue",
        "total_sales_profit",
        "total_repairs_profit",
    ).first()

    if not summary:
        return Decimal("0"), Decimal("0")

    total_revenue = summary.total_sales_revenue + summary.total_repairs_revenue
    total_profit = summary.total_sales_profit + summary.total_repairs_profit
    return total_revenue, total_profit
