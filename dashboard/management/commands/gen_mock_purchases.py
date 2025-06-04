from django.core.management.base import BaseCommand
from inventory.models import Purchase, Product, Supplier
from faker import Faker
import random
from django.utils import timezone
from decimal import Decimal

class Command(BaseCommand):
    help = 'Generate 3 mock purchases for testing.'

    def handle(self, *args, **kwargs):
        fake = Faker('th_TH')
        products = list(Product.objects.all())
        suppliers = list(Supplier.objects.all())
        if not products or not suppliers:
            self.stdout.write(self.style.ERROR('ต้องมีสินค้าและซัพพลายเออร์ในฐานข้อมูลก่อน'))
            return
        statuses = ['RECEIVED', 'RECEIVED', 'PENDING']
        for i in range(3):
            product = random.choice(products)
            supplier = random.choice(suppliers)
            quantity = random.randint(1, 10)
            price = Decimal(str(round(random.uniform(100, 1000), 2)))
            purchase_date = timezone.now()
            payment = random.choice(['PAID', 'UNPAID'])
            status = statuses[i]
            purchase = Purchase.objects.create(
                product=product,
                quantity=quantity,
                price=price,
                supplier=supplier,
                purchase_date=purchase_date,
                payment=payment,
                status=status
            )
            self.stdout.write(self.style.SUCCESS(f'Created purchase: {product.name} x{quantity} ({status}) จาก {supplier.name} ราคา {price}'))
