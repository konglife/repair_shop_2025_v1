from django.db import models, transaction
from customers.models import Customer
from inventory.models import Product
from django.utils import timezone
from .services import calculate_sale_item_price, update_stock_after_sale

# รายการสินค้าที่ขาย
class SaleItem(models.Model):
    sale = models.ForeignKey('Sale', on_delete=models.CASCADE, related_name='items', verbose_name="การขาย")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sold_items', verbose_name="สินค้า")
    quantity = models.PositiveIntegerField(verbose_name="จำนวน")
    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="ราคาต่อหน่วย")

    @property
    def total_price(self):
        return self.quantity * self.price

    @transaction.atomic
    def save(self, *args, **kwargs):
        # ดึงราคาจาก Product อัตโนมัติ
        self.price = calculate_sale_item_price(self)
        self._skip_post_save_stock_update = True
        super().save(*args, **kwargs)
        del self._skip_post_save_stock_update
        update_stock_after_sale(self)


    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Sale ID: {self.sale.id})"


# การขาย
class Sale(models.Model):
    PAYMENT_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name='sales', verbose_name="ลูกค้า")
    sale_date = models.DateTimeField(default=timezone.now, verbose_name="วันที่ขาย")
    note = models.TextField(blank=True, null=True, verbose_name="หมายเหตุ")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0, verbose_name="ยอดรวม")
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNPAID', verbose_name="การชำระเงิน")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตเมื่อ")

    def calculate_total_amount(self):
        # คำนวณยอดรวมจาก SaleItem ทั้งหมดที่เชื่อมโยงกับการขายนี้
        total = sum(item.total_price for item in self.items.all())
        self.total_amount = total
        return total

    def delete(self, *args, **kwargs):
        # คืนจำนวนสินค้าในสต็อกก่อนที่จะลบการขาย
        for item in self.items.all(): item.delete()

        # ลบการขายหลังจากคืนสต็อกแล้ว
        super(Sale, self).delete(*args, **kwargs)

    def __str__(self):
        return f"Sale ID: {self.id} to {self.customer.name if self.customer else 'Unknown Customer'}"
