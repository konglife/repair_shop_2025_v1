# customers/models.py
from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)  # ชื่อและนามสกุล
    phone = models.CharField(max_length=15)  # เบอร์โทรศัพท์
    email = models.EmailField(unique=True)  # อีเมล
    address = models.TextField()  # ที่อยู่
    created_at = models.DateTimeField(auto_now_add=True)  # วันเวลาที่สร้าง
    updated_at = models.DateTimeField(auto_now=True)  # วันเวลาที่แก้ไขล่าสุด

    def __str__(self):
        return f"{self.name}"

