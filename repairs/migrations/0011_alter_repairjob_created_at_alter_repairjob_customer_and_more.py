# Generated by Django 5.2.1 on 2025-06-12 11:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_alter_customer_address_alter_customer_created_at_and_more'),
        ('inventory', '0009_alter_category_name_alter_product_category_and_more'),
        ('repairs', '0010_alter_repairjob_labor_charge_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repairjob',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='สร้างเมื่อ'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repair_jobs', to='customers.customer', verbose_name='ลูกค้า'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='description',
            field=models.TextField(verbose_name='รายละเอียด'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='job_name',
            field=models.CharField(max_length=255, verbose_name='ชื่องาน'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='labor_charge',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='ค่าแรง'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='หมายเหตุ'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='parts_cost_total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='ค่าอะไหล่'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='payment',
            field=models.CharField(choices=[('PAID', 'Paid'), ('UNPAID', 'Unpaid')], default='UNPAID', max_length=20, verbose_name='การชำระเงิน'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='repair_date',
            field=models.DateTimeField(verbose_name='วันที่ซ่อม'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='status',
            field=models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='IN_PROGRESS', max_length=20, verbose_name='สถานะ'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='รวมทั้งหมด'),
        ),
        migrations.AlterField(
            model_name='repairjob',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='อัปเดตเมื่อ'),
        ),
        migrations.AlterField(
            model_name='usedpart',
            name='cost_price_per_unit',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=10, verbose_name='ราคาต่อหน่วย'),
        ),
        migrations.AlterField(
            model_name='usedpart',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='สร้างเมื่อ'),
        ),
        migrations.AlterField(
            model_name='usedpart',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='used_in_repairs', to='inventory.product', verbose_name='อะไหล่'),
        ),
        migrations.AlterField(
            model_name='usedpart',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='จำนวน'),
        ),
        migrations.AlterField(
            model_name='usedpart',
            name='repair_job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='used_parts', to='repairs.repairjob', verbose_name='งานซ่อม'),
        ),
    ]
