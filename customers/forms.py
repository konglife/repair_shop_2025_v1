from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'profile_image', 'phone', 'email', 'address']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Customer.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Customer name already exists.")
        return name

# class RepairHistoryForm(forms.ModelForm):
#     class Meta:
#         model = RepairHistory
#         fields = ['customer', 'description', 'date', 'cost']
