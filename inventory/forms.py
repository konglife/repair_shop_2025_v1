# inventory/forms.py
from django import forms
from .models import Purchase, Supplier

class PurchaseForm(forms.ModelForm):
    price = forms.DecimalField(label='ราคาซื้อ (ต่อหน่วย)', required=True, min_value=0, help_text='กรุณากรอกราคาซื้อของสินค้าในแต่ละล็อต')
    class Meta:
        model = Purchase
        fields = ['product', 'quantity', 'price', 'supplier', 'purchase_date', 'payment', 'status']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = '__all__'  # หรือกำหนดฟิลด์ที่ต้องการ