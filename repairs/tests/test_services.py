from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from customers.models import Customer
from inventory.models import Category, Unit, Product, Supplier, Purchase
from repairs.models import RepairJob, UsedPart
from repairs import services


class ServiceLayerTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat")
        self.unit = Unit.objects.create(name="Unit")
        self.product = Product.objects.create(
            name="Prod",
            category=self.category,
            unit=self.unit,
            selling_price=Decimal("100"),
        )
        self.supplier = Supplier.objects.create(name="Supp", contact_info="c")
        self.customer = Customer.objects.create(
            name="Cust", phone="0", email="c@example.com", address="addr"
        )

    def create_purchase(self, price: Decimal, quantity: int = 1):
        return Purchase.objects.create(
            product=self.product,
            quantity=quantity,
            price=price,
            supplier=self.supplier,
            purchase_date=timezone.now(),
            payment="PAID",
            status="RECEIVED",
        )

    def test_calculate_repair_total(self):
        job = RepairJob(labor_charge=Decimal("50"), parts_cost_total=Decimal("20"))
        total = services.calculate_repair_total(job)
        self.assertEqual(total, Decimal("70"))

    def test_assign_used_part_cost_with_history(self):
        self.create_purchase(Decimal("10"), 5)
        self.create_purchase(Decimal("20"), 5)
        job = RepairJob.objects.create(
            job_name="Fix",
            customer=self.customer,
            repair_date=timezone.now(),
            description="d",
            labor_charge=Decimal("0"),
        )
        part = UsedPart(repair_job=job, product=self.product, quantity=2)
        services.assign_used_part_cost(part)
        self.assertEqual(part.cost_price_per_unit, Decimal("15"))
        self.assertEqual(part.total_cost, Decimal("30"))

    def test_assign_used_part_cost_zero_quantity(self):
        self.create_purchase(Decimal("10"), 1)
        job = RepairJob.objects.create(
            job_name="Fix",
            customer=self.customer,
            repair_date=timezone.now(),
            description="d",
            labor_charge=Decimal("0"),
        )
        part = UsedPart(repair_job=job, product=self.product, quantity=0)
        services.assign_used_part_cost(part)
        self.assertEqual(part.cost_price_per_unit, Decimal("10"))
        self.assertEqual(part.total_cost, Decimal("0"))

    def test_assign_used_part_cost_no_history(self):
        job = RepairJob.objects.create(
            job_name="Fix",
            customer=self.customer,
            repair_date=timezone.now(),
            description="d",
            labor_charge=Decimal("0"),
        )
        part = UsedPart(repair_job=job, product=self.product, quantity=1)
        services.assign_used_part_cost(part)
        self.assertEqual(part.cost_price_per_unit, Decimal("0"))
        self.assertEqual(part.total_cost, Decimal("0"))

