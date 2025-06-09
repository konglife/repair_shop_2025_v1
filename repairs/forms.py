from django import forms
from .models import RepairJob, UsedPart
from .services import calculate_parts_cost


class UsedPartForm(forms.ModelForm):
    class Meta:
        model = UsedPart
        fields = ["product", "quantity"]


class RepairJobForm(forms.ModelForm):
    class Meta:
        model = RepairJob
        fields = ["total_amount"]

    def clean_total_amount(self):
        total = self.cleaned_data.get("total_amount")
        parts_cost = sum(
            calculate_parts_cost(up.product, up.quantity)
            for up in self.instance.used_parts.all()
        )
        if total is not None and total < parts_cost:
            raise forms.ValidationError(
                f"Total amount ({total}) must be \u2265 parts cost ({parts_cost})."
            )
        return total
