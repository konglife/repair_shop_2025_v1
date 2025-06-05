# sales/apps.py
from django.apps import AppConfig

class SalesConfig(AppConfig):
    name = 'sales'

    def ready(self):
        import importlib
        importlib.import_module('sales.signals')  # นำเข้าเพื่อให้ Django โหลดสัญญาณ
