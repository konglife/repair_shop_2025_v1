from django.test import TestCase, RequestFactory
from django.utils import timezone
from decimal import Decimal
from django.contrib.auth.models import User

from .models import (
    Category,
    Unit,
    Product,
    Supplier,
    Stock,
    Purchase,
)
from .signals import update_stock_status
from . import views
import json

class SignalTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Cat")
        self.unit = Unit.objects.create(name="U")
        self.product = Product.objects.create(
            name="Prod", category=self.category, unit=self.unit, selling_price=100
        )
        self.supplier = Supplier.objects.create(name="Supp", contact_info="c")

    def create_purchase(self, **kwargs):
        data = {
            "product": self.product,
            "quantity": 5,
            "price": Decimal("10.00"),
            "supplier": self.supplier,
            "purchase_date": timezone.now(),
            "payment": "PAID",
            "status": "RECEIVED",
        }
        data.update(kwargs)
        return Purchase.objects.create(**data)

    def test_update_stock_status(self):
        stock = Stock.objects.create(product=self.product, min_stock=3, current_stock=2)
        update_stock_status(stock)
        self.assertEqual(stock.status, "LOW")
        stock.current_stock = 0
        update_stock_status(stock)
        self.assertEqual(stock.status, "OUT_OF_STOCK")
        stock.current_stock = 5
        update_stock_status(stock)
        self.assertEqual(stock.status, "AVAILABLE")

    def test_create_purchase_updates_stock(self):
        self.create_purchase(quantity=10, price=Decimal("20.00"))
        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.current_stock, 10)
        self.assertEqual(stock.average_cost, Decimal("20.00"))

    def test_update_purchase_status_to_cancelled(self):
        p = self.create_purchase(quantity=4)
        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.current_stock, 4)
        p.status = "CANCELLED"
        p.save()
        stock.refresh_from_db()
        self.assertEqual(stock.current_stock, 0)

    def test_update_purchase_quantity_change(self):
        p = self.create_purchase(quantity=3, price=Decimal("15.00"))
        stock = Stock.objects.get(product=self.product)
        self.assertEqual(stock.current_stock, 3)
        p.quantity = 6
        p.save()
        stock.refresh_from_db()
        self.assertEqual(stock.current_stock, 6)


class ViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="u", password="p")
        self.category = Category.objects.create(name="Tools")
        self.unit = Unit.objects.create(name="Piece")
        self.product = Product.objects.create(
            name="Hammer", category=self.category, unit=self.unit, selling_price=Decimal("50.00")
        )
        self.stock = Stock.objects.create(
            product=self.product, current_stock=8, min_stock=0, average_cost=Decimal("25.00")
        )
        if not hasattr(Product, "description"):
            Product.description = property(lambda self: self.notes)

    def test_product_list_view_returns_stock_and_price(self):
        request = self.factory.get("/products/")
        request.user = self.user
        resp = views.product_list(request)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["products"][0]["current_stock"], 8)
        self.assertEqual(data["products"][0]["price"], float(self.product.selling_price))

    def test_product_detail_view(self):
        request = self.factory.get(f"/products/{self.product.id}/")
        request.user = self.user
        resp = views.product_detail(request, pk=self.product.id)
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.content)
        self.assertEqual(data["stock"]["quantity"], 8)
        self.assertEqual(data["price"], float(self.product.selling_price))
