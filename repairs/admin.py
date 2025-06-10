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
    readonly_fields = ('parts_cost_total',)
    fields = ('job_name', 'customer', 'repair_date', 'description', 'status', 'notes', 'payment', 'total_amount', 'parts_cost_total')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # หลังจากบันทึก UsedPart inline แล้ว ให้เรียก update_parts_cost เพื่ออัปเดต parts_cost_total
        form.instance.update_parts_cost()
        # บันทึก RepairJob อีกครั้งเพื่อให้ labor_charge ถูกคำนวณใหม่ด้วย parts_cost_total ที่อัปเดตแล้ว
        form.instance.save()


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

