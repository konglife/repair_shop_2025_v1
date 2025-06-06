from django.db import models
from django.utils import timezone

# Create your models here.

class MonthlySummary(models.Model):
    """
    สรุปข้อมูลรายเดือน อิงโครงสร้างจาก DailySummary
    - month: เดือน (format YYYY-MM)
    - year: ปี (optional, redundancy for query)
    """
    month = models.CharField(max_length=7, unique=True, help_text="เดือนที่สรุปข้อมูล เช่น 2025-06")
    year = models.PositiveIntegerField(default=timezone.now().year, help_text="ปี ค.ศ.")
    total_sales_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_repairs_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False)
    total_repairs_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    total_sales_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="ต้นทุนรวมของการขายสินค้า")
    total_sales_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="กำไรรวมจากการขายสินค้า (รายรับขาย - ต้นทุนขาย)")
    total_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="กำไรรวมทั้งหมด (ขาย+ซ่อม)")
    total_labor_charge = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="ค่าแรงรวมจากงานซ่อม")
    total_parts_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="ต้นทุนอะไหล่รวมของงานซ่อม")
    sales_count = models.PositiveIntegerField(default=0)
    repairs_completed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    repair_profit_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="% กำไรงานซ่อม")
    top_repairs = models.TextField(blank=True, default="[]", help_text="Top 5 งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด (JSON string)")

    class Meta:
        verbose_name = "Monthly Summary"
        verbose_name_plural = "Monthly Summaries"
        ordering = ['-month']

    def save(self, *args, **kwargs):
        # คำนวณ total_revenue และ total_profit อัตโนมัติ
        self.total_revenue = self.total_sales_revenue + self.total_repairs_revenue
        self.total_profit = self.total_sales_profit + self.total_repairs_profit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Summary for {self.month}"

class DailySummary(models.Model):
    date = models.DateField(unique=True, default=timezone.now)
    total_sales_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_repairs_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    # หมายเหตุ: กำไรส่วนนี้คิดเฉพาะจากงานซ่อม (รายรับซ่อม - ต้นทุนอะไหล่) ยังไม่รวมกำไรจากการขายสินค้าโดยตรง
    total_repairs_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # ฟิลด์ใหม่ตามแผนการทำงานเฟส 3.5
    total_sales_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="ต้นทุนรวมของการขายสินค้า")
    total_sales_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="กำไรรวมจากการขายสินค้า (รายรับขาย - ต้นทุนขาย)")
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="กำไรรวมทั้งหมด (ขาย+ซ่อม)")
    total_labor_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="ค่าแรงรวมจากงานซ่อม (สำหรับวิเคราะห์สัดส่วนค่าแรงและชิ้นส่วน)")
    total_parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="ต้นทุนอะไหล่รวมของงานซ่อม")
    # ฟิลด์เดิม
    sales_count = models.PositiveIntegerField(default=0)
    repairs_completed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    repair_profit_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="% กำไรงานซ่อม")
    top_repairs = models.TextField(blank=True, default="[]", help_text="Top 5 งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด (JSON string)")

    class Meta:
        verbose_name = "Daily Summary"
        verbose_name_plural = "Daily Summaries"
        ordering = ['-date'] # เรียงลำดับตามวันที่ล่าสุดก่อน

    def save(self, *args, **kwargs):
        # คำนวณ total_revenue อัตโนมัติ
        self.total_revenue = self.total_sales_revenue + self.total_repairs_revenue
        # คำนวณ total_profit อัตโนมัติ
        self.total_profit = self.total_sales_profit + self.total_repairs_profit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Summary for {self.date.strftime('%Y-%m-%d')}"
