from django.core.management.base import BaseCommand
from customers.models import Customer
from faker import Faker

class Command(BaseCommand):
    help = 'Generate 3 mock customers for testing.'

    def handle(self, *args, **kwargs):
        fake = Faker('th_TH')
        for _ in range(3):
            name = fake.name()
            phone = fake.phone_number()
            email = fake.unique.email()
            address = fake.address().replace('\n', ' ')
            customer = Customer.objects.create(
                name=name,
                phone=phone,
                email=email,
                address=address
            )
            self.stdout.write(self.style.SUCCESS(f'Created customer: {customer.name} ({customer.email})'))
