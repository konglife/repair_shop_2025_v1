from django.contrib import admin
from .models import DailySummary, MonthlySummary

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'total_sales_revenue',
        'total_repairs_revenue',
        'total_revenue',
        'total_repairs_profit',
        'total_sales_cost',
        'total_sales_profit',
        'total_profit',
        'total_labor_charge',
        'total_parts_cost',
        'sales_count',
        'repairs_completed_count',
        'repair_profit_percent',
        'created_at',
        'updated_at',
    )
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

@admin.register(MonthlySummary)
class MonthlySummaryAdmin(admin.ModelAdmin):
    list_display = (
        'month',
        'year',
        'total_sales_revenue',
        'total_repairs_revenue',
        'total_revenue',
        'total_repairs_profit',
        'total_sales_cost',
        'total_sales_profit',
        'total_profit',
        'total_labor_charge',
        'total_parts_cost',
        'sales_count',
        'repairs_completed_count',
        'repair_profit_percent',
        'created_at',
        'updated_at',
    )
    list_filter = ('month', 'year')
    search_fields = ('month', 'year')
    ordering = ('-month',)
    readonly_fields = ('created_at', 'updated_at', 'total_parts_cost')

    fieldsets = (
        (None, {
            'fields': ('month', 'year')
        }),
        ('Revenue & Profit', {
            'fields': (
                'total_sales_revenue',
                'total_repairs_revenue',
                'total_revenue',
                'total_repairs_profit',
                'total_sales_cost',
                'total_sales_profit',
                'total_profit',
                'total_labor_charge',
                'total_parts_cost',
                'repair_profit_percent',
            )
        }),
        ('Counts', {
            'fields': ('sales_count', 'repairs_completed_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
