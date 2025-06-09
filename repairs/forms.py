from django import forms

from .models import RepairJob, UsedPart
from .services import calculate_parts_cost


class UsedPartForm(forms.ModelForm):
    class Meta:
        model = UsedPart
        fields = ["product", "quantity"]


class RepairJobForm(forms.ModelForm):
    total_amount = forms.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = RepairJob
        fields = [
            "job_name",
            "customer",
            "repair_date",
            "description",
            "status",
            "notes",
            "payment",
        ]

    def __init__(self, *args, used_parts=None, **kwargs):
        self.used_parts = used_parts or []
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        total_amount = cleaned_data.get("total_amount") or 0
        parts_cost = sum(
            calculate_parts_cost(part["product"], part.get("quantity", 1))
            for part in self.used_parts
        )
        if total_amount < parts_cost:
            raise forms.ValidationError("Total amount must be at least parts cost.")
        return cleaned_data
