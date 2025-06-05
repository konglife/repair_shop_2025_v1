import os
import tempfile
from django.test import TestCase
from customers.models import Customer

class DummyImage:
    def __init__(self, path):
        self.path = path

class CustomerSignalTests(TestCase):
    def test_delete_without_profile_image(self):
        customer = Customer.objects.create(name='X', phone='1', email='x@example.com', address='addr')
        try:
            customer.delete()
        except Exception as e:
            self.fail(f"Signal raised unexpected exception: {e}")

    def test_delete_removes_profile_image_file(self):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(b'data')
        tmp.flush()
        tmp.close()
        customer = Customer.objects.create(name='Y', phone='1', email='y@example.com', address='addr')
        customer.profile_image = DummyImage(tmp.name)
        customer.delete()
        self.assertFalse(os.path.exists(tmp.name))
