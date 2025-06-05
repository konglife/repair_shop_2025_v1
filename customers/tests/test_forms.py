from django.test import TestCase
from customers.forms import CustomerForm
from customers.models import Customer


class CustomerFormTests(TestCase):
    def test_duplicate_name_invalid(self):
        Customer.objects.create(name='Sam', phone='1', email='sam@example.com', address='addr')
        form = CustomerForm(data={
            'name': 'Sam',
            'phone': '2',
            'email': 'sam2@example.com',
            'address': 'addr2'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_unique_name_valid(self):
        form = CustomerForm(data={
            'name': 'Unique',
            'phone': '3',
            'email': 'u@example.com',
            'address': 'addr'
        })
        self.assertTrue(form.is_valid())

    def test_update_same_name_valid(self):
        customer = Customer.objects.create(name='Jane', phone='4', email='jane@example.com', address='addr')
        form = CustomerForm(data={
            'name': 'Jane',
            'phone': '4',
            'email': 'jane@example.com',
            'address': 'addr'
        }, instance=customer)
        self.assertTrue(form.is_valid())
