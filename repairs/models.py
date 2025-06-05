# repairs/models.py
from django.db import models
from customers.models import Customer
from inventory.models import Product
from repairs.utils.cost_calculation import calculate_historical_weighted_average_cost, update_repair_job_costs

# งานซ่อมหลัก
class RepairJob(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    PAYMENT_CHOICES = [
        ('PAID', 'Paid'),
        ('UNPAID', 'Unpaid'),
    ]

    job_name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='repair_jobs')
    repair_date = models.DateTimeField()
    description = models.TextField()
    labor_charge = models.DecimalField(max_digits=10, decimal_places=2)
    parts_cost_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    notes = models.TextField(blank=True, null=True)
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_parts_cost(self):
        update_repair_job_costs(self)

    def save(self, *args, **kwargs):
        # คำนวณ total_amount ทุกครั้งก่อนบันทึก
        self.total_amount = self.labor_charge + self.parts_cost_total
        super(RepairJob, self).save(*args, **kwargs)

    def __str__(self):
        return f"Repair Job for {self.customer.name}"

# อะไหล่ที่ใช้ในงานซ่อม
class UsedPart(models.Model):
    repair_job = models.ForeignKey(RepairJob, on_delete=models.CASCADE, related_name='used_parts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='used_in_repairs')
    quantity = models.PositiveIntegerField()
    cost_price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.cost_price_per_unit = calculate_historical_weighted_average_cost(self.product)
        super(UsedPart, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.repair_job.job_name}"
