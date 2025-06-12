from django.db import models, transaction
from django.utils import timezone

# Create your models here.

class MonthlySummary(models.Model):
    """
    สรุปข้อมูลรายเดือน อิงโครงสร้างจาก DailySummary
    - month: เดือน (format YYYY-MM)
    - year: ปี (optional, redundancy for query)
    """
    month = models.CharField(max_length=7, unique=True, help_text="เดือนที่สรุปข้อมูล เช่น 2025-06", verbose_name="เดือน")
    year = models.PositiveIntegerField(default=timezone.now().year, help_text="ปี ค.ศ.", verbose_name="ปี")
    total_sales_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="รายรับจากการขายสินค้า")
    total_repairs_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="รายรับจากงานซ่อม")
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0, editable=False, verbose_name="รายรับรวมทั้งหมด")
    total_repairs_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0, verbose_name="กำไรจากงานซ่อม")
    total_sales_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="ต้นทุนรวมของการขายสินค้า", verbose_name="ต้นทุนสินค้า")
    total_sales_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="กำไรรวมจากการขายสินค้า (รายรับขาย - ต้นทุนขาย)", verbose_name="กำไรจากการขายสินค้า")
    total_profit = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="กำไรรวมทั้งหมด (ขาย+ซ่อม)", verbose_name="กำไรรวมทั้งหมด")
    total_parts_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0, help_text="ต้นทุนอะไหล่รวมของงานซ่อม", verbose_name="ต้นทุนอะไหล่ซ่อม")
    sales_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนรายการขาย")
    repairs_completed_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนงานซ่อมเสร็จสิ้น")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตเมื่อ")
    repair_profit_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="% กำไรงานซ่อม", verbose_name="% กำไรงานซ่อม")
    top_repairs = models.TextField(blank=True, default="[]", help_text="Top 5 งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด (JSON string)", verbose_name="งานซ่อมยอดนิยม")

    class Meta:
        verbose_name = "Monthly Summary"
        verbose_name_plural = "Monthly Summaries"
        ordering = ['-month']

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Calculate total_revenue and total_profit from the instance's attributes
        self.total_revenue = self.total_sales_revenue + self.total_repairs_revenue
        self.total_profit = self.total_sales_profit + self.total_repairs_profit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Summary for {self.month}"

class DailySummary(models.Model):
    date = models.DateField(unique=True, default=timezone.now, verbose_name="วันที่")
    total_sales_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="รายรับจากการขายสินค้า")
    total_repairs_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="รายรับจากงานซ่อม")
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False, verbose_name="รายรับรวมทั้งหมด")
    # หมายเหตุ: กำไรส่วนนี้คิดเฉพาะจากงานซ่อม (รายรับซ่อม - ต้นทุนอะไหล่) ยังไม่รวมกำไรจากการขายสินค้าโดยตรง
    total_repairs_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="กำไรจากงานซ่อม")
    # ฟิลด์ใหม่ตามแผนการทำงานเฟส 3.5
    total_sales_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="ต้นทุนรวมของการขายสินค้า", verbose_name="ต้นทุนสินค้า")
    total_sales_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="กำไรรวมจากการขายสินค้า (รายรับขาย - ต้นทุนขาย)", verbose_name="กำไรจากการขายสินค้า")
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="กำไรรวมทั้งหมด (ขาย+ซ่อม)", verbose_name="กำไรรวมทั้งหมด")
    total_parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="ต้นทุนอะไหล่รวมของงานซ่อม", verbose_name="ต้นทุนอะไหล่ซ่อม")
    # ฟิลด์เดิม
    sales_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนรายการขาย")
    repairs_completed_count = models.PositiveIntegerField(default=0, verbose_name="จำนวนงานซ่อมเสร็จสิ้น")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="อัปเดตเมื่อ")
    repair_profit_percent = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="% กำไรงานซ่อม", verbose_name="% กำไรงานซ่อม")
    top_repairs = models.TextField(blank=True, default="[]", help_text="Top 5 งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด (JSON string)", verbose_name="งานซ่อมยอดนิยม")

    class Meta:
        verbose_name = "Daily Summary"
        verbose_name_plural = "Daily Summaries"
        ordering = ['-date'] # เรียงลำดับตามวันที่ล่าสุดก่อน

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Calculate total_revenue and total_profit from the instance's attributes
        self.total_revenue = self.total_sales_revenue + self.total_repairs_revenue
        self.total_profit = self.total_sales_profit + self.total_repairs_profit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Summary for {self.date.strftime('%Y-%m-%d')}"
