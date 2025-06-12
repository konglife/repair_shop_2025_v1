# customers/models.py
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100, verbose_name="ชื่อและนามสกุล")  # ชื่อและนามสกุล
    phone = models.CharField(max_length=15, verbose_name="เบอร์โทรศัพท์")  # เบอร์โทรศัพท์
    email = models.EmailField(unique=True, verbose_name="อีเมล")  # อีเมล
    address = models.TextField(verbose_name="ที่อยู่")  # ที่อยู่
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันเวลาที่สร้าง")  # วันเวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True, verbose_name="วันเวลาที่แก้ไขล่าสุด")  # วันเวลาที่แก้ไขล่าสุด

    def __str__(self):
        return f"{self.name}"

