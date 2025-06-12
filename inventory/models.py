# inventory/models.py
from django.db import models, transaction
from django.utils import timezone

from .services import calculate_purchase_total, update_stock_after_purchase

# ซัพพลายเออร์
class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อ") #
    contact_info = models.TextField(verbose_name="ข้อมูลการติดต่อ")
    url = models.URLField(blank=True, null=True, verbose_name="URL")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันเวลาที่สร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="วันเวลาที่แก้ไขล่าสุด")

    def __str__(self):
        return self.name

# หมวดหมู่สินค้า (แยกต่างหากสำหรับความยืดหยุ่น)
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="ชื่อหมวดหมู่")

    def __str__(self):
        return self.name

# หน่วย (แยกต่างหากสำหรับความยืดหยุ่น)
class Unit(models.Model):
    name = models.CharField(max_length=50, verbose_name="หน่วย")

    def __str__(self):
        return self.name

# สินค้า
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อสินค้า")
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="รูปภาพ")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name="หมวดหมู่")
    unit = models.ForeignKey('Unit', on_delete=models.SET_NULL, null=True, verbose_name="หน่วย")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาขาย")
    notes = models.TextField(blank=True, null=True, verbose_name="หมายเหตุ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันเวลาที่สร้าง")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="วันเวลาที่แก้ไขล่าสุด")

    def __str__(self):
        return self.name

# สต็อกสินค้า
class Stock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stocks', verbose_name="สินค้า")
    min_stock = models.IntegerField(default=0, verbose_name="สต็อกขั้นต่ำ")
    current_stock = models.IntegerField(default=0, verbose_name="สต็อกปัจจุบัน")
    status = models.CharField(
        max_length=20,
        choices=[('AVAILABLE', 'Available'), ('LOW', 'Low'), ('OUT_OF_STOCK', 'Out of Stock')],
        default='AVAILABLE',
        verbose_name="สถานะ"
    )
    last_updated_at = models.DateTimeField(default=timezone.now, verbose_name="วันเวลาที่อัปเดตล่าสุด")
    average_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="ราคาเฉลี่ย")

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases', verbose_name="สินค้า")
    quantity = models.IntegerField(verbose_name="จำนวนที่สั่งซื้อ")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="ราคาต่อหน่วย")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchases', verbose_name="ซัพพลายเออร์")
    purchase_date = models.DateTimeField(verbose_name="วันที่สั่งซื้อ")
    payment = models.CharField(max_length=20, choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid')], verbose_name="การชำระเงิน")
    status = models.CharField(max_length=20, choices=[('PENDING', 'Pending'), ('RECEIVED', 'Received'), ('CANCELLED', 'Cancelled')], verbose_name="สถานะ")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False, verbose_name="ราคารวม")

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
