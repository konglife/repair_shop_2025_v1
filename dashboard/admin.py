from django.contrib import admin
from .models import DailySummary

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_revenue', 'total_repairs_profit', 'total_parts_cost', 'sales_count', 'repairs_completed_count', 'created_at', 'updated_at')
    list_filter = ('date',)
    search_fields = ('date',)
    ordering = ('-date',) # เรียงจากล่าสุดไปเก่าสุด
    readonly_fields = ('created_at', 'updated_at', 'total_parts_cost') # ไม่ควรแก้ไขเวลาสร้าง/อัปเดต

    fieldsets = (
        (None, {
            'fields': ('date',)
        }),
        ('Revenue & Profit', {
            'fields': ('total_sales_revenue', 'total_repairs_revenue', 'total_revenue', 'total_repairs_profit', 'total_parts_cost')
        }),
        ('Counts', {
            'fields': ('sales_count', 'repairs_completed_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # ซ่อนไว้เป็น default
        }),
    )

# ถ้าต้องการ Register แบบง่ายๆ ใช้บรรทัดนี้แทน @admin.register(...) และ class ... ข้างบน
# admin.site.register(DailySummary)
