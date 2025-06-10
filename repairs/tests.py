from django.test import TestCase, RequestFactory
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

from customers.models import Customer
from inventory.models import Category, Unit, Product, Supplier, Stock, Purchase
from repairs.models import RepairJob, UsedPart
from repairs.utils.cost_calculation import calculate_historical_weighted_average_cost


class CostCalculationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat")
        self.unit = Unit.objects.create(name="Unit")
        self.product = Product.objects.create(
            name="Prod",
            category=self.category,
            unit=self.unit,
            selling_price=Decimal("100.00"),
        )
        self.supplier = Supplier.objects.create(name="Supp", contact_info="c")

    def create_purchase(self, **kwargs):
        data = {
            "product": self.product,
            "quantity": 1,
            "price": Decimal("10"),
            "supplier": self.supplier,
            "purchase_date": timezone.now(),
            "payment": "PAID",
            "status": "RECEIVED",
        }
        data.update(kwargs)
        return Purchase.objects.create(**data)

    def test_weighted_average_cost_handles_missing_price(self):
        self.create_purchase(quantity=5, price=Decimal("10"))
        self.create_purchase(quantity=5, price=Decimal("20"))
        # สร้าง purchase ที่ราคาเป็น None โดยอัปเดตในฐานข้อมูลหลังบันทึก
        p = self.create_purchase(quantity=2, price=Decimal("0"))
        Purchase.objects.filter(pk=p.pk).update(price=None)
        cost = calculate_historical_weighted_average_cost(self.product)
        self.assertEqual(cost, Decimal("12.5"))


class RepairJobModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Customer", phone="123", email="test@example.com")

    def test_save_calculates_labor_charge(self):
        # Test that labor_charge is calculated correctly on save based on total_amount and parts_cost_total
        job = RepairJob.objects.create(
            job_name="Test Job",
            customer=self.customer,
            repair_date=timezone.now(),
            description="Test Description",
            total_amount=Decimal("120.00"), # User inputs total_amount
            parts_cost_total=Decimal("70.00"),
            status="IN_PROGRESS",
        )
        job.refresh_from_db()
        # labor_charge should be total_amount - parts_cost_total
        self.assertEqual(job.labor_charge, Decimal("50.00"))

    def test_labor_charge_is_editable_false(self):
        # Test that labor_charge is not editable
        field = RepairJob._meta.get_field('labor_charge')
        self.assertFalse(field.editable)

    def test_total_amount_is_editable_true(self):
        # Test that total_amount is editable
        field = RepairJob._meta.get_field('total_amount')
        self.assertTrue(field.editable)


class UsedPartSignalTests(TestCase):
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
        Purchase.objects.create(
            product=self.product,
            quantity=5,
            price=Decimal("10"),
            supplier=self.supplier,
            purchase_date=timezone.now(),
            payment="PAID",
            status="RECEIVED",
        )
        Purchase.objects.create(
            product=self.product,
            quantity=5,
            price=Decimal("20"),
            supplier=self.supplier,
            purchase_date=timezone.now(),
            payment="PAID",
            status="RECEIVED",
        )
        # สต็อกจะถูกสร้างโดยสัญญาณของ Purchase
        self.stock = Stock.objects.get(product=self.product)
        self.customer = Customer.objects.create(
            name="Cust", phone="0", email="c@example.com", address="addr"
        )
        self.job = RepairJob.objects.create(
            job_name="Fix",
            customer=self.customer,
            repair_date=timezone.now(),
            description="d",
            total_amount=Decimal("100.00"), # ตั้งค่า total_amount แทน labor_charge
            status="COMPLETED",
        )

    def test_used_part_save_updates_job_and_stock(self):
        part = UsedPart.objects.create(repair_job=self.job, product=self.product, quantity=3)
        part.refresh_from_db()
        self.stock.refresh_from_db()
        self.job.refresh_from_db()
        # ตรวจสอบ cost_price_per_unit ควรเป็น average_cost จาก Stock (15 บาท)
        self.assertEqual(part.cost_price_per_unit, Decimal("15.00"))
        # ตรวจสอบ current_stock ควรลดลง 3 ชิ้น (จาก 10 เหลือ 7)
        self.assertEqual(self.stock.current_stock, 7)
        # ตรวจสอบ parts_cost_total ควรเป็น 3 ชิ้น * 15 บาท = 45 บาท
        self.assertEqual(self.job.parts_cost_total, Decimal("45.00"))
        # ตรวจสอบ labor_charge ควรเป็น total_amount (100) - parts_cost_total (45) = 55 บาท
        self.assertEqual(self.job.labor_charge, Decimal("55.00"))
        # total_amount ถูกกำหนดไว้ใน setup
        self.assertEqual(self.job.total_amount, Decimal("100.00"))

    def test_used_part_delete_returns_stock(self):
        part = UsedPart.objects.create(repair_job=self.job, product=self.product, quantity=2)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 8)
        part.delete()
        self.stock.refresh_from_db()
        self.job.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 10)
        self.assertEqual(self.job.parts_cost_total, Decimal("0"))

    def test_status_change_adjusts_stock(self):
        job = RepairJob.objects.create(
            job_name="A",
            customer=self.customer,
            repair_date=timezone.now(),
            description="d",
            labor_charge=Decimal("0"),
            status="IN_PROGRESS",
        )
        UsedPart.objects.create(repair_job=job, product=self.product, quantity=2)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 10)
        job.status = "COMPLETED"
        job.save()
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 8)
        job.status = "IN_PROGRESS"
        job.save()
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 10)
