from django import forms
from .models import RepairJob
from .services import calculate_parts_cost

class RepairJobForm(forms.ModelForm):
    total_amount = forms.DecimalField(min_value=0)

    class Meta:
        model = RepairJob
        fields = [
            'job_name',
            'customer',
            'repair_date',
            'description',
            'status',
            'notes',
            'payment',
        ]

    def save(self, commit=True):
        self.instance.total_amount = self.cleaned_data['total_amount']
        return super().save(commit=commit)

    def clean_total_amount(self):
        total = self.cleaned_data.get('total_amount')
        parts_cost = sum(
            calculate_parts_cost(part.product, part.quantity)
            for part in self.instance.used_parts.all()
        )
        if total is not None and total < parts_cost:
            raise forms.ValidationError(
                'Total amount must be greater than or equal to the parts cost.'
            )
        return total
