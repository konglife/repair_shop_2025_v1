from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from .models import Purchase, Stock
from django.utils import timezone
from decimal import Decimal

# Helper function for updating stock status
def update_stock_status(stock):
    """ฟังก์ชันช่วยในการอัปเดตสถานะของสต็อก"""
    if stock.current_stock == 0:
        stock.status = 'OUT_OF_STOCK'
    elif stock.current_stock < stock.min_stock:
        stock.status = 'LOW'
    else:
        stock.status = 'AVAILABLE'

# Helper function to encapsulate complex stock and cost update logic
def _handle_stock_and_cost_on_purchase_update(old_purchase, new_purchase):
    """
    Handles stock and average cost updates based on changes in a Purchase instance.
    This function encapsulates the complex logic previously in the pre_save signal.
    """
    product = new_purchase.product
    stock, created = Stock.objects.get_or_create(product=product)
    if created:
        # Initialize new stock if it was just created
        stock.min_stock = 0
        stock.current_stock = 0 # Start with 0, then add the new_purchase.quantity
        stock.average_cost = Decimal('0.00') # Will be updated by the logic below

    # Case 1: Status changed from RECEIVED to PENDING or CANCELLED
    if old_purchase.status == 'RECEIVED' and new_purchase.status != 'RECEIVED':
        stock.current_stock -= old_purchase.quantity

    # Case 2: Status changed from PENDING or CANCELLED to RECEIVED
    elif old_purchase.status != 'RECEIVED' and new_purchase.status == 'RECEIVED':
        stock.current_stock += new_purchase.quantity
        # Recalculate average_cost (Moving Average)
        total_cost = (stock.current_stock * stock.average_cost) + \
                     (new_purchase.quantity * (new_purchase.price or Decimal('0.00')))
        total_qty = stock.current_stock + new_purchase.quantity
        stock.average_cost = (total_cost / total_qty) if total_qty > 0 else Decimal('0.00')

    # Case 3: Quantity updated while status remains RECEIVED
    elif old_purchase.status == 'RECEIVED' and new_purchase.status == 'RECEIVED' and \
         old_purchase.quantity != new_purchase.quantity:
        # Adjust stock for the old quantity first
        stock.current_stock -= old_purchase.quantity
        # Add stock for the new quantity
        stock.current_stock += new_purchase.quantity
        # Recalculate average_cost (Moving Average)
        total_cost = (stock.current_stock * stock.average_cost) + \
                     (new_purchase.quantity * (new_purchase.price or Decimal('0.00')))
        total_qty = stock.current_stock + new_purchase.quantity
        stock.average_cost = (total_cost / total_qty) if total_qty > 0 else Decimal('0.00')

    stock.last_updated_at = timezone.now()
    update_stock_status(stock)
    stock.save()

@receiver(post_save, sender=Purchase)
def update_stock_after_purchase(sender, instance, created, **kwargs):
    product = instance.product

    # อัปเดต Stock เมื่อมีการสร้าง Purchase ใหม่และสถานะเป็น RECEIVED
    if created and instance.status == 'RECEIVED':
        stock, created = Stock.objects.get_or_create(product=product)
        if created:
            stock.min_stock = 0
            stock.current_stock = instance.quantity
            # กรณีแรกที่รับเข้า: average_cost = ราคาซื้อ
            stock.average_cost = instance.price or Decimal('0.00')
        else:
            # Moving Average: (stock เดิม + ของใหม่) / (จำนวนเดิม + จำนวนใหม่)
            total_cost = (stock.current_stock * stock.average_cost) + (instance.quantity * (instance.price or Decimal('0.00')))
            total_qty = stock.current_stock + instance.quantity
            stock.current_stock += instance.quantity
            stock.average_cost = (total_cost / total_qty) if total_qty > 0 else Decimal('0.00')
        stock.last_updated_at = timezone.now()
        update_stock_status(stock)
        stock.save()

@receiver(post_delete, sender=Purchase)
def update_stock_after_purchase_delete(sender, instance, **kwargs):
    # ปรับสต็อกเมื่อมีการลบ Purchase ที่เคยถูกเพิ่มเข้าไป
    if instance.status == 'RECEIVED':
        product = instance.product
        try:
            stock = Stock.objects.get(product=product)
            stock.current_stock -= instance.quantity
            stock.last_updated_at = timezone.now()
            update_stock_status(stock)
            stock.save()
        except Stock.DoesNotExist:
            pass

@receiver(pre_save, sender=Purchase)
def update_stock_before_purchase_update(sender, instance, **kwargs):
    if instance.pk:  # ตรวจสอบว่าเป็นการอัปเดต (มี pk อยู่แล้ว)
        old_purchase = Purchase.objects.get(pk=instance.pk)
        # Call the helper function to handle the complex logic
        _handle_stock_and_cost_on_purchase_update(old_purchase, instance)
