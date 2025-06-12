# customers/admin.py
from django.contrib import admin
from .models import Customer

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name' , 'address' , 'email', 'phone', 'created_at')  # ตัด profile_thumbnail ออก
    search_fields = ('name', 'email', 'phone')  # เพิ่มฟังก์ชันการค้นหาตามชื่อ อีเมล และเบอร์โทรศัพท์
    list_filter = ('created_at',)  # เพิ่มตัวกรองตามวันที่สร้าง
    ordering = ('-created_at',)  # เรียงตามวันที่สร้างใหม่ล่าสุดก่อน
    fields = ('name', 'phone', 'email', 'address')  # ตัด profile_image ออก

# class RepairHistoryAdmin(admin.ModelAdmin):
#     list_display = ('customer', 'description', 'date', 'cost')
#     search_fields = ('customer__name', 'description')
#     list_filter = ('date',)
#     ordering = ('-date',)

admin.site.register(Customer, CustomerAdmin)
# admin.site.register(RepairHistory, RepairHistoryAdmin)