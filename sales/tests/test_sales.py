from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings

from customers.models import Customer
from inventory.models import Category, Unit, Product, Stock
from sales.models import Sale, SaleItem

class SaleItemSignalTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat")
        self.unit = Unit.objects.create(name="Unit")
        self.product = Product.objects.create(
            name="Prod",
            category=self.category,
            unit=self.unit,
            selling_price=Decimal("50.00"),
        )
        self.stock = Stock.objects.create(product=self.product, current_stock=10)
        self.customer = Customer.objects.create(
            name="Cust",
            phone="0",
            email="c@example.com",
            address="addr",
        )
        self.sale = Sale.objects.create(customer=self.customer)

    def test_sale_item_creation_updates_stock_and_total(self):
        item = SaleItem.objects.create(
            sale=self.sale, product=self.product, quantity=2
        )
        self.stock.refresh_from_db()
        self.sale.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 8)
        self.assertEqual(self.sale.total_amount, Decimal("100.00"))
        self.assertEqual(item.price, self.product.selling_price)
        self.assertEqual(item.total_price, Decimal("100.00"))

    def test_sale_item_update_adjusts_stock_and_total(self):
        item = SaleItem.objects.create(
            sale=self.sale, product=self.product, quantity=1
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 9)
        item.quantity = 3
        item.save()
        self.stock.refresh_from_db()
        self.sale.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 7)
        self.assertEqual(self.sale.total_amount, Decimal("150.00"))

    def test_sale_item_delete_returns_stock(self):
        item = SaleItem.objects.create(
            sale=self.sale, product=self.product, quantity=2
        )
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 8)
        item.delete()
        self.stock.refresh_from_db()
        self.sale.save()  # trigger post_save signal to recalc total
        self.sale.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 10)
        self.assertEqual(self.sale.total_amount, Decimal("0"))

    def test_sale_delete_cascades_item_deletes(self):
        item = SaleItem.objects.create(
            sale=self.sale, product=self.product, quantity=1
        )
        self.sale.delete()
        self.assertFalse(SaleItem.objects.filter(pk=item.pk).exists())
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.current_stock, 10)


@override_settings(ROOT_URLCONF="sales.urls")
class IndexViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="pass")

    def test_index_requires_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_index_returns_message_when_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode(), {"message": "Sales API endpoint"}
        )
