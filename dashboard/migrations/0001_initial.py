# Generated by Django 5.1.2 on 2025-04-05 15:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0002_delete_repairhistory'),
        ('inventory', '0006_purchase_total_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('date', models.DateField(unique=True)),
                ('repair_jobs_count', models.IntegerField(default=0)),
                ('sales_count', models.IntegerField(default=0)),
                ('revenue_repair', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('revenue_sales', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost_repair', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cost_sales', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('profit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('new_customers', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomerInsights',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_repair_jobs', models.IntegerField(default=0)),
                ('total_sales', models.IntegerField(default=0)),
                ('total_spent', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('avg_repair_value', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('first_visit_date', models.DateField(blank=True, null=True)),
                ('latest_visit_date', models.DateField(blank=True, null=True)),
                ('visit_frequency_days', models.IntegerField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('customer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='customers.customer')),
            ],
        ),
        migrations.CreateModel(
            name='InventoryAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(choices=[('LOW_STOCK', 'สินค้าใกล้หมด'), ('OUT_OF_STOCK', 'สินค้าหมด'), ('REORDER', 'ควรสั่งซื้อเพิ่ม')], max_length=20)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
        ),
        migrations.CreateModel(
            name='MonthlySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('repair_jobs_count', models.IntegerField(default=0)),
                ('sales_count', models.IntegerField(default=0)),
                ('revenue_repair', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('revenue_sales', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('cost_repair', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('cost_sales', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('profit', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('new_customers', models.IntegerField(default=0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'unique_together': {('year', 'month')},
            },
        ),
        migrations.CreateModel(
            name='ProductStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sales_quantity', models.IntegerField(default=0)),
                ('total_repair_usage', models.IntegerField(default=0)),
                ('last_sale_date', models.DateField(blank=True, null=True)),
                ('last_repair_usage_date', models.DateField(blank=True, null=True)),
                ('total_sales_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('avg_profit_per_unit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('product', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='inventory.product')),
            ],
        ),
    ]
