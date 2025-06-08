# inventory/models.py
from django.db import models, transaction
from django.utils import timezone

from .services import calculate_purchase_total, update_stock_after_purchase

# ซัพพลายเออร์
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_info = models.TextField()  # ข้อมูลการติดต่อ เช่น อีเมล, เบอร์โทรศัพท์
    url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# หมวดหมู่สินค้า (แยกต่างหากสำหรับความยืดหยุ่น)
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# หน่วย (แยกต่างหากสำหรับความยืดหยุ่น)
class Unit(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# สินค้า
class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # ราคาขาย
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# สต็อกสินค้า
class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks')
    min_stock = models.IntegerField(default=0)
    current_stock = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[('AVAILABLE', 'Available'), ('LOW', 'Low'), ('OUT_OF_STOCK', 'Out of Stock')],
        default='AVAILABLE'
    )
    last_updated_at = models.DateTimeField(default=timezone.now)  # เพิ่ม default ให้กับ last_updated_at
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # เพิ่มฟิลด์นี้

    def __str__(self):
        return f"Stock of {self.product.name}: {self.current_stock} (Status: {self.get_status()})"

    def get_status(self):
        if self.current_stock == 0:
            return 'OUT_OF_STOCK'
        elif self.current_stock < self.min_stock:
            return 'LOW'
        else:
            return 'AVAILABLE'

# การสั่งซื้อสินค้า
class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    quantity = models.IntegerField()  # จำนวนที่สั่งซื้อ
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # ราคาต่อหน่วย (ยอมรับ NULL ได้)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases')
    purchase_date = models.DateTimeField()
    payment = models.CharField(max_length=20, choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid')])
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('RECEIVED', 'Received'), ('CANCELLED', 'Cancelled')])
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)  # เพิ่ม default=0

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        # preserve original logic by delegating to service layer
        is_new = self.pk is None
        self.total_price = calculate_purchase_total(self)
        self._skip_post_save_stock_update = True
        super().save(*args, **kwargs)
        del self._skip_post_save_stock_update
        if is_new:
            update_stock_after_purchase(self)

    def __str__(self):
        return f"Purchase of {self.product.name} from {self.supplier.name}"
