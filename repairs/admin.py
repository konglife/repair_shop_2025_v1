# repairs/admin.py
from django.contrib import admin
from .models import RepairJob, UsedPart

# การตั้งค่าหน้า Admin สำหรับ RepairJob
class UsedPartInline(admin.TabularInline):
    model = UsedPart
    extra = 1
    readonly_fields = ('cost_price_per_unit', 'created_at')

class RepairJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'job_name', 'customer', 'repair_date', 'labor_charge', 
                   'parts_cost_total', 'total_amount', 'status', 'payment', 'updated_at')
    search_fields = ('customer__name', 'description', 'notes')
    list_filter = ('status', 'payment', 'repair_date', 'updated_at')
    ordering = ('-updated_at',)
    inlines = [UsedPartInline]
    readonly_fields = ('total_amount', 'parts_cost_total',)

    def save_model(self, request, obj, form, change):
        # คำนวณค่า total_amount ก่อนบันทึก
        obj.total_amount = obj.labor_charge + obj.parts_cost_total
        super().save_model(request, obj, form, change)

# การตั้งค่าหน้า Admin สำหรับ UsedPart
class UsedPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'repair_job', 'product', 'quantity', 'cost_price_per_unit', 'created_at')
    search_fields = ('repair_job__job_name', 'product__name')
    list_filter = ('created_at', 'repair_job__status')
    readonly_fields = ('cost_price_per_unit', 'created_at')
    ordering = ('-created_at',)

# ลงทะเบียนกับหน้า Admin
admin.site.register(RepairJob, RepairJobAdmin)
admin.site.register(UsedPart, UsedPartAdmin)

