# sales/apps.py
from django.apps import AppConfig

class SalesConfig(AppConfig):
    name = 'sales'

    def ready(self):
        import sales.signals  # นำเข้า signals เพื่อเชื่อมต่อ signal
