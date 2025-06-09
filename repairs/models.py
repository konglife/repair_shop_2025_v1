# repairs/models.py
from django.db import models, transaction
from customers.models import Customer
from inventory.models import Product
from repairs.utils.cost_calculation import update_repair_job_costs
from .services import calculate_repair_total, apply_used_part_cost

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

    @transaction.atomic
    def save(self, *args, **kwargs):
        from .services import calculate_parts_cost, compute_labor_from_total

        # 1) Calculate total parts cost
        parts = self.used_parts.all() if self.pk else []
        parts_cost = sum(
            calculate_parts_cost(up.product, up.quantity)
            for up in parts
        )
        # 2) User-supplied total_amount remains unchanged
        # 3) Compute labor_charge
        self.labor_charge = compute_labor_from_total(self.total_amount, parts_cost)
        # 4) Store parts_cost_total
        self.parts_cost_total = parts_cost
        if "update_fields" in kwargs and kwargs["update_fields"]:
            fields = set(kwargs["update_fields"])
            fields.update({"parts_cost_total", "labor_charge"})
            kwargs["update_fields"] = list(fields)
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

    @transaction.atomic
    def save(self, *args, **kwargs):
        # คงไว้ซึ่งตรรกะเดิมโดยเรียก apply_used_part_cost
        total_cost = apply_used_part_cost(self)
        self.cost_price_per_unit = total_cost / self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for {self.repair_job.job_name}"
