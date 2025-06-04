from django import template
from decimal import Decimal
from datetime import timedelta

register = template.Library()

@register.filter
def percentage(value, total):
    """
    คำนวณเปอร์เซ็นต์จาก value/total
    ใช้งาน: {{ value|percentage:total }}
    """
    try:
        value = Decimal(value)
        total = Decimal(total)
        if total == 0:
            return 0
        return round((value / total) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def add_days(value, days):
    """
    เพิ่มหรือลดจำนวนวันใน datetime object
    ใช้งาน: {{ value|add_days:-1 }} หรือ {{ value|add_days:7 }}
    """
    try:
        return value + timedelta(days=int(days))
    except:
        return value 