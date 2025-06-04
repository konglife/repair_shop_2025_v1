# customers/apps.py
from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customers'

    def ready(self):
        import customers.signals  # เชื่อมต่อ signal
