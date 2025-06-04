# dashboard/management/commands/generate_daily_summary.py

import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Sum, Count, F, DecimalField, Avg
from datetime import timedelta # เพิ่ม timedelta
from django.db.models.functions import Coalesce
from django.conf import settings
import logging
import json

from dashboard.models import DailySummary
from sales.models import Sale, SaleItem
from repairs.models import RepairJob

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'ทำการสร้างหรืออัปเดตข้อมูลสรุปรายวัน (DailySummary) สำหรับวันที่ระบุ'

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='วันที่ต้องการสร้างรายงาน (format: YYYY-MM-DD)')
        parser.add_argument('--force', action='store_true', help='บังคับให้สร้างใหม่แม้จะมีข้อมูลอยู่แล้ว')

    def handle(self, *args, **options):
        # กำหนดวันที่จะสร้างรายงาน (ถ้าไม่ระบุจะใช้วันที่เมื่อวาน)
        date_str = options.get('date')
        force = options.get('force', False)
        
        if date_str:
            try:
                report_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stderr.write(self.style.ERROR(f'รูปแบบวันที่ไม่ถูกต้อง: {date_str}'))
                return
        else:
            # ใช้วันที่เมื่อวาน
            report_date = timezone.now().date() - timedelta(days=1)
        
        self.stdout.write(f'กำลังสร้างรายงานสรุปสำหรับวันที่: {report_date}')
        
        # ตรวจสอบว่ามีรายงานนี้อยู่แล้วหรือไม่
        existing_summary = DailySummary.objects.filter(date=report_date).first()
        if existing_summary and not force:
            self.stdout.write(self.style.WARNING(f'มีรายงานสรุปสำหรับวันที่ {report_date} อยู่แล้ว ใช้ --force เพื่อสร้างใหม่'))
            return
        
        # รวบรวมข้อมูลยอดขายสำหรับวันนี้
        sales_data = Sale.objects.filter(
            sale_date__date=report_date,
            payment='PAID'
        ).aggregate(
            total_sales=Coalesce(Sum('total_amount'), 0, output_field=DecimalField()),
            count=Count('id')
        )
        
        # คำนวณต้นทุนการขายสินค้า
        sales_items = SaleItem.objects.filter(
            sale__sale_date__date=report_date,
            sale__payment='PAID'
        )
        
        total_sales_cost = 0
        for item in sales_items:
            if item.product:
                # ใช้ average_cost จาก stock ถ้ามี ไม่เช่นนั้นเป็น 0
                stock = item.product.stocks.first()
                avg_cost = stock.average_cost if stock else 0
                total_sales_cost += item.quantity * avg_cost
        
        # คำนวณกำไรจากการขายสินค้า
        total_sales_profit = sales_data['total_sales'] - total_sales_cost
        
        # รวบรวมข้อมูลงานซ่อม
        repairs_data = RepairJob.objects.filter(
            repair_date__date=report_date,
            status='COMPLETED'
        ).aggregate(
            total_repairs_revenue=Coalesce(Sum('total_amount'), 0, output_field=DecimalField()),
            total_parts_cost=Coalesce(Sum('parts_cost_total'), 0, output_field=DecimalField()),
            total_labor_charge=Coalesce(Sum('labor_charge'), 0, output_field=DecimalField()),
            repairs_completed_count=Count('id')
        )
        total_repairs_revenue = repairs_data['total_repairs_revenue']
        total_parts_cost = repairs_data['total_parts_cost']
        total_labor_charge = repairs_data['total_labor_charge']
        repairs_completed_count = repairs_data['repairs_completed_count']

        # คำนวณกำไรจากงานซ่อม
        total_repairs_profit = total_repairs_revenue - total_parts_cost

        # คำนวณ % กำไรงานซ่อม
        repair_profit_percent = (total_repairs_profit / total_repairs_revenue * 100) if total_repairs_revenue else 0
        # Top 5 งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด
        top_repairs_qs = RepairJob.objects.filter(repair_date__date=report_date, status='COMPLETED')\
            .values('job_name')\
            .annotate(count=Count('id'), amount=Sum('total_amount'))\
            .order_by('-amount', '-count')[:5]
        top_repairs = [
            {'name': r['job_name'], 'count': r['count'], 'amount': float(r['amount'])} for r in top_repairs_qs
        ]

        # สร้างหรืออัปเดตรายงานสรุป
        if existing_summary:
            summary = existing_summary
        else:
            summary = DailySummary(date=report_date)
        
        # อัปเดตข้อมูล
        summary.total_sales_revenue = sales_data['total_sales']
        summary.total_repairs_revenue = total_repairs_revenue
        summary.total_repairs_profit = total_repairs_profit
        summary.sales_count = sales_data['count']
        summary.repairs_completed_count = repairs_completed_count
        summary.total_sales_cost = total_sales_cost
        summary.total_sales_profit = total_sales_profit
        summary.total_labor_charge = total_labor_charge
        summary.total_parts_cost = total_parts_cost  # เพิ่มบันทึกต้นทุนอะไหล่ซ่อม
        summary.repair_profit_percent = repair_profit_percent
        summary.top_repairs = json.dumps(top_repairs, ensure_ascii=False)
        # total_revenue และ total_profit คำนวณอัตโนมัติใน save()
        
        summary.save()
        
        self.stdout.write(self.style.SUCCESS(
            f'สร้างรายงานสรุปสำเร็จ: รายรับรวม {summary.total_revenue} บาท '
            f'(ขาย: {summary.total_sales_revenue} บาท, ซ่อม: {summary.total_repairs_revenue} บาท), '
            f'กำไรรวม {summary.total_profit} บาท'
        ))

        # แสดงผลลัพธ์
        self.stdout.write(f"  - ยอดขายสินค้า: {summary.total_sales_revenue} บาท")
        self.stdout.write(f"  - ต้นทุนสินค้า: {summary.total_sales_cost} บาท")
        self.stdout.write(f"  - กำไรจากการขาย: {summary.total_sales_profit} บาท")
        self.stdout.write(f"  - รายได้จากงานซ่อม: {summary.total_repairs_revenue} บาท")
        self.stdout.write(f"  - กำไรจากงานซ่อม: {summary.total_repairs_profit} บาท")
        self.stdout.write(f"  - รายได้ค่าแรง: {summary.total_labor_charge} บาท")
        self.stdout.write(f"  - รายได้รวมทั้งหมด: {summary.total_revenue} บาท")
        self.stdout.write(f"  - กำไรรวมทั้งหมด: {summary.total_profit} บาท")
        self.stdout.write(f"  - จำนวนรายการขาย: {summary.sales_count} รายการ")
        self.stdout.write(f"  - จำนวนงานซ่อมเสร็จสิ้น: {summary.repairs_completed_count} งาน")
        self.stdout.write(f"  - % กำไรงานซ่อม: {summary.repair_profit_percent:.2f}%")
        self.stdout.write(f"  - งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด: {summary.top_repairs}")