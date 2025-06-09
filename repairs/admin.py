from django.contrib import admin
from django import forms
from .models import RepairJob, UsedPart


class UsedPartInline(admin.TabularInline):
    model = UsedPart
    extra = 1
    readonly_fields = ('cost_price_per_unit', 'created_at')


@admin.register(RepairJob)
class RepairJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'parts_cost_total', 'labor_charge', 'status')
    readonly_fields = ('parts_cost_total', 'labor_charge')
    inlines = [UsedPartInline]

    def get_form(self, request, obj=None, **kwargs):
        fields = [f.name for f in self.model._meta.fields if f.editable and f.name != 'total_amount']
        form = super().get_form(request, obj, fields=fields, **kwargs)
        if 'total_amount' not in form.base_fields:
            form.base_fields['total_amount'] = forms.DecimalField()
        if 'labor_charge' in form.base_fields:
            form.base_fields['labor_charge'].disabled = True
        return form

    def save_model(self, request, obj, form, change):
        if obj.total_amount < obj.parts_cost_total:
            from django.core.exceptions import ValidationError
            raise ValidationError({
                'total_amount': f"Total amount ({obj.total_amount}) must be \u2265 parts cost ({obj.parts_cost_total})."
            })
        super().save_model(request, obj, form, change)


class UsedPartAdmin(admin.ModelAdmin):
    list_display = ('id', 'repair_job', 'product', 'quantity', 'cost_price_per_unit', 'created_at')
    search_fields = ('repair_job__job_name', 'product__name')
    list_filter = ('created_at', 'repair_job__status')
    readonly_fields = ('cost_price_per_unit', 'created_at')
    ordering = ('-created_at',)


admin.site.register(UsedPart, UsedPartAdmin)
