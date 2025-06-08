# sales/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import SaleItem, Sale

@receiver(pre_save, sender=SaleItem)
def pre_save_sale_item_quantity(sender, instance, **kwargs):
    if instance.pk: # Only for existing instances
        try:
            old_instance = SaleItem.objects.get(pk=instance.pk)
            instance._old_quantity = old_instance.quantity
        except SaleItem.DoesNotExist:
            instance._old_quantity = 0 # New instance or not found
    else:
        instance._old_quantity = 0 # New instance

@receiver(post_save, sender=SaleItem)
def post_save_sale_item_stock_adjustment(sender, instance, created, **kwargs):
    if not getattr(instance, '_skip_post_save_stock_update', False):
        stock = instance.product.stocks.first()
        if stock:
            if created:  # New SaleItem created
                stock.current_stock -= instance.quantity
            else:  # Existing SaleItem updated
                quantity_difference = instance.quantity - instance._old_quantity
                stock.current_stock -= quantity_difference
            stock.save()

    # After stock adjustment, update the total amount of the associated Sale
    # This ensures the Sale's total is correct immediately after its SaleItems are saved
    instance.sale.calculate_total_amount()
    instance.sale.save(update_fields=['total_amount'])

@receiver(post_delete, sender=SaleItem)
def update_stock_on_delete(sender, instance, **kwargs):
    # เมื่อ SaleItem ถูกลบ จะคืนจำนวนสินค้าในสต็อก
    stock = instance.product.stocks.first()
    if stock:
        stock.current_stock += instance.quantity
        stock.save()

@receiver(post_save, sender=Sale)
def post_save_sale_total_amount(sender, instance, created, **kwargs):
    # คำนวณยอดรวมใหม่หลังจาก SaleItem ถูกบันทึกหรือลบ
    # และบันทึก Sale อีกครั้งเพื่ออัปเดต total_amount
    old_total_amount = instance.total_amount
    instance.calculate_total_amount()
    if old_total_amount != instance.total_amount:
        instance.save(update_fields=['total_amount'])

