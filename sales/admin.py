# sales/admin.py
from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'sale_date', 'total_amount', 'payment', 'updated_at')
    list_filter = ('customer', 'payment', 'sale_date')
    search_fields = ('customer__name', 'note')
    inlines = [SaleItemInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:  # เมื่อกำลังดูหรือแก้ไขรายการที่มีอยู่แล้ว
            return ['updated_at']  # นำ created_at ออกจาก readonly fields
        return []