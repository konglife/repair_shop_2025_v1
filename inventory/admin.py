# inventory/admin.py
from django.contrib import admin
from .models import Supplier, Category, Product, Stock, Purchase, Unit
from .forms import PurchaseForm

# ซัพพลายเออร์
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_info', 'url', 'created_at', 'updated_at')  # แสดงฟิลด์ในหน้า List
    search_fields = ('name', 'contact_info')  # เพิ่มการค้นหาตามชื่อและข้อมูลติดต่อ
    list_filter = ('created_at',)  # เพิ่มตัวกรองตามวันที่สร้าง
    ordering = ('-created_at',)  # เรียงลำดับตามวันที่สร้างใหม่ล่าสุดก่อน

# หมวดหมู่สินค้า
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# หน่วยสินค้า
class UnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# สินค้า
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image', 'category', 'unit', 'selling_price', 'notes', 'created_at', 'updated_at')
    search_fields = ('name', 'category__name', 'unit__name')  # เพิ่มการค้นหาตามชื่อสินค้า หมวดหมู่ และหน่วย
    list_filter = ('category', 'created_at')  # กรองตามหมวดหมู่และวันที่สร้าง
    ordering = ('-created_at',)  # เรียงลำดับตามวันที่สร้างใหม่ล่าสุดก่อน

# สต็อกสินค้า
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'current_stock', 'min_stock', 'average_cost', 'get_status', 'last_updated_at')
    search_fields = ('product__name',)
    list_filter = ('last_updated_at',)
    ordering = ('-last_updated_at',)
    readonly_fields = ('product', 'last_updated_at', 'average_cost')  # average_cost เป็น readonly

    def get_status(self, obj):
        return obj.get_status()  # เรียกใช้ฟังก์ชัน get_status() จาก Model
    get_status.short_description = 'สถานะสต็อก'

# การสั่งซื้อสินค้า
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    list_display = ('id', 'product', 'quantity', 'price', 'supplier', 'purchase_date', 'status', 'payment', 'total_price')
    search_fields = ('product__name', 'supplier__name',)
    list_filter = ('status', 'payment', 'purchase_date')
    ordering = ('-purchase_date',)
    readonly_fields = ('total_price',)  # เพิ่ม readonly_fields ที่เกี่ยวข้องกับ Purchase

# ลงทะเบียน Model กับ Django Admin
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Unit, UnitAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(Purchase, PurchaseAdmin)
