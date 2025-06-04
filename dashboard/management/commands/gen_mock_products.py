from django.core.management.base import BaseCommand
from inventory.models import Product, Category, Unit
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Generate 5 mock products for testing.'

    def handle(self, *args, **kwargs):
        fake = Faker('th_TH')
        # สร้างหมวดหมู่และหน่วยถ้ายังไม่มี
        categories = list(Category.objects.all())
        if not categories:
            for cname in ['อะไหล่ไฟฟ้า', 'อะไหล่เครื่องยนต์', 'อุปกรณ์เสริม']:
                categories.append(Category.objects.create(name=cname))
        units = list(Unit.objects.all())
        if not units:
            self.stdout.write(self.style.ERROR('No units found in database. กรุณาเพิ่มหน่วยสินค้าก่อน'))
            return
        product_names = [
            'หลอดไฟหน้า', 'แบตเตอรี่', 'ผ้าเบรก', 'น้ำมันเครื่อง', 'ฟิวส์',
            'กรองอากาศ', 'สายพาน', 'หัวเทียน', 'ยางรถยนต์', 'น้ำยาหล่อเย็น',
            'ไส้กรองน้ำมัน', 'ปั๊มน้ำ', 'สายไฟ', 'แผ่นคลัช', 'ลูกปืนล้อ'
        ]
        used_names = set()
        for _ in range(5):
            # สุ่มชื่อสินค้าไม่ซ้ำ
            available_names = [n for n in product_names if n not in used_names]
            if not available_names:
                break
            name = random.choice(available_names)
            used_names.add(name)
            category = random.choice(categories)
            unit = random.choice(units)
            selling_price = round(random.uniform(50, 500), 2)
            product = Product.objects.create(
                name=name,
                category=category,
                unit=unit,
                selling_price=selling_price
            )
            self.stdout.write(self.style.SUCCESS(f'Created product: {product.name} ({category.name}, {unit.name}) ราคา {selling_price}'))
