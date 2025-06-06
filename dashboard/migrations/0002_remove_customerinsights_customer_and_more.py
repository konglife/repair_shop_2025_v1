# Generated by Django 5.1.2 on 2025-04-09 11:50

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerinsights',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='inventoryalert',
            name='product',
        ),
        migrations.DeleteModel(
            name='MonthlySummary',
        ),
        migrations.RemoveField(
            model_name='productstatistics',
            name='product',
        ),
        migrations.AlterModelOptions(
            name='dailysummary',
            options={'ordering': ['-date'], 'verbose_name': 'Daily Summary', 'verbose_name_plural': 'Daily Summaries'},
        ),
        migrations.RenameField(
            model_name='dailysummary',
            old_name='last_updated',
            new_name='updated_at',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='cost_repair',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='cost_sales',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='new_customers',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='profit',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='repair_jobs_count',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='revenue_repair',
        ),
        migrations.RemoveField(
            model_name='dailysummary',
            name='revenue_sales',
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='repairs_completed_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='total_repairs_profit',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='total_repairs_revenue',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='total_revenue',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=12),
        ),
        migrations.AddField(
            model_name='dailysummary',
            name='total_sales_revenue',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12),
        ),
        migrations.AlterField(
            model_name='dailysummary',
            name='date',
            field=models.DateField(default=django.utils.timezone.now, unique=True),
        ),
        migrations.AlterField(
            model_name='dailysummary',
            name='sales_count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='CustomerInsights',
        ),
        migrations.DeleteModel(
            name='InventoryAlert',
        ),
        migrations.DeleteModel(
            name='ProductStatistics',
        ),
    ]
