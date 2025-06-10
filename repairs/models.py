# repairs/models.py
from decimal import Decimal
from django.db import models, transaction
from django.db.models import Sum, F
from customers.models import Customer
from inventory.models import Product
from .services import apply_used_part_cost

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
    labor_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)
    parts_cost_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # now editable, user input
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN_PROGRESS')
    notes = models.TextField(blank=True, null=True)
    payment = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='UNPAID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_parts_cost(self):
        """Recalculates and updates the parts_cost_total based on associated UsedPart instances."""
        total_cost = self.used_parts.aggregate(
            total=Sum(F('quantity') * F('cost_price_per_unit'), output_field=models.DecimalField())
        )['total'] or Decimal('0.00')
        self.parts_cost_total = total_cost

    def save(self, *args, **kwargs):
        # Recalculate labor_charge before saving.
        if self.total_amount is not None and self.parts_cost_total is not None:
            self.labor_charge = self.total_amount - self.parts_cost_total
        super().save(*args, **kwargs)

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
        # apply_used_part_cost sets the cost_price_per_unit on this instance.
        apply_used_part_cost(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.repair_job.job_name}"
