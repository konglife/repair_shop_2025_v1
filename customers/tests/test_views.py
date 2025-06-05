from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse

from customers.models import Customer


@override_settings(ROOT_URLCONF='customers.tests.urls')
class DeleteCustomerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='pass')

    def test_get_not_allowed(self):
        self.client.force_login(self.user)
        customer = Customer.objects.create(name='A', phone='111', email='a@example.com', address='Addr')
        url = reverse('customers:delete_customer', args=[customer.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Customer.objects.filter(pk=customer.pk).exists())

    def test_delete_customer_post_success(self):
        self.client.force_login(self.user)
        customer = Customer.objects.create(name='B', phone='222', email='b@example.com', address='Addr')
        url = reverse('customers:delete_customer', args=[customer.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode(), {
            'success': True,
            'message': 'Customer deleted successfully'
        })
        self.assertFalse(Customer.objects.filter(pk=customer.pk).exists())
