# dashboard/management/commands/generate_monthly_summary.py

import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from dashboard.models import MonthlySummary, DailySummary
from decimal import Decimal

class Command(BaseCommand):
    help = 'สร้างหรืออัปเดตข้อมูลสรุปรายเดือน (MonthlySummary) สำหรับเดือนที่ระบุ หรือย้อนหลังหลายเดือน'

    def add_arguments(self, parser):
        parser.add_argument('--month', type=str, help='เดือนที่ต้องการสร้างรายงาน (format: YYYY-MM)')
        parser.add_argument('--months-back', type=int, default=1, help='จำนวนเดือนย้อนหลัง (default=1)')
        parser.add_argument('--force', action='store_true', help='บังคับให้สร้างใหม่แม้จะมีข้อมูลอยู่แล้ว')

    def handle(self, *args, **options):
        month_str = options.get('month')
        months_back = options.get('months_back', 1)
        force = options.get('force', False)

        today = timezone.now().date()
        months = []

        if month_str:
            try:
                dt = datetime.datetime.strptime(month_str, '%Y-%m').date()
                months = [(dt.year, dt.month)]
            except ValueError:
                self.stderr.write(self.style.ERROR(f'รูปแบบเดือนไม่ถูกต้อง: {month_str}'))
                return
        else:
            # Default: generate for previous N months
            ref = today.replace(day=1)
            for i in range(months_back):
                m = (ref.month - i - 1) % 12 + 1
                y = ref.year - ((ref.month - i - 1) // 12)
                months.append((y, m))
            months.reverse()

        for year, month in months:
            month_label = f"{year:04d}-{month:02d}"
            start = datetime.date(year, month, 1)
            if month == 12:
                end = datetime.date(year+1, 1, 1)
            else:
                end = datetime.date(year, month+1, 1)

            self.stdout.write(f'\nสร้างรายงานสรุปสำหรับเดือน: {month_label}')
            existing = MonthlySummary.objects.filter(month=month_label).first()
            if existing and not force:
                self.stdout.write(self.style.WARNING(f'มีรายงานสรุปสำหรับเดือน {month_label} อยู่แล้ว ใช้ --force เพื่อสร้างใหม่'))
                continue

            qs = DailySummary.objects.filter(date__gte=start, date__lt=end)
            agg = qs.aggregate(
                total_sales_revenue=Coalesce(Sum('total_sales_revenue', output_field=DecimalField()), Decimal('0.00')),
                total_sales_cost=Coalesce(Sum('total_sales_cost', output_field=DecimalField()), Decimal('0.00')),
                total_sales_profit=Coalesce(Sum('total_sales_profit', output_field=DecimalField()), Decimal('0.00')),
                sales_count=Coalesce(Sum('sales_count', output_field=IntegerField()), 0),
                total_repairs_revenue=Coalesce(Sum('total_repairs_revenue', output_field=DecimalField()), Decimal('0.00')),
                total_parts_cost=Coalesce(Sum('total_parts_cost', output_field=DecimalField()), Decimal('0.00')),
                total_repairs_profit=Coalesce(Sum('total_repairs_profit', output_field=DecimalField()), Decimal('0.00')),
                repairs_completed_count=Coalesce(Sum('repairs_completed_count', output_field=IntegerField()), 0),
            )
            total_revenue = agg['total_sales_revenue'] + agg['total_repairs_revenue']
            total_profit = agg['total_sales_profit'] + agg['total_repairs_profit']

            repair_profit_percent = Decimal('0.00')
            if agg['total_repairs_revenue'] > 0:
                repair_profit_percent = (agg['total_repairs_profit'] / agg['total_repairs_revenue']) * Decimal('100.00')

            # Create or update MonthlySummary
            summary, created = MonthlySummary.objects.update_or_create(
                month=month_label,
                defaults={
                    'year': year,
                    'total_sales_revenue': agg['total_sales_revenue'],
                    'total_sales_cost': agg['total_sales_cost'],
                    'total_sales_profit': agg['total_sales_profit'],
                    'sales_count': agg['sales_count'],
                    'total_repairs_revenue': agg['total_repairs_revenue'],
                    'total_parts_cost': agg['total_parts_cost'],
                    'total_repairs_profit': agg['total_repairs_profit'],
                    'repairs_completed_count': agg['repairs_completed_count'],
                    'total_revenue': total_revenue,
                    'total_profit': total_profit,
                    'repair_profit_percent': repair_profit_percent,
                }
            )
            msg = 'สร้างใหม่' if created else 'อัปเดต'
            self.stdout.write(self.style.SUCCESS(f'{msg} MonthlySummary สำเร็จ: เดือน {month_label}'))
            self.stdout.write(f'  - รายรับรวม: {total_revenue:,.2f} บาท (ขาย: {agg["total_sales_revenue"]:,.2f}, ซ่อม: {agg["total_repairs_revenue"]:,.2f})')
            self.stdout.write(f'  - กำไรรวม: {total_profit:,.2f} บาท (ขาย: {agg["total_sales_profit"]:,.2f}, ซ่อม: {agg["total_repairs_profit"]:,.2f})')
            self.stdout.write(f'  - จำนวนขาย: {agg["sales_count"]} | งานซ่อมเสร็จสิ้น: {agg["repairs_completed_count"]}')
            self.stdout.write(f'  - ต้นทุนสินค้า: {agg["total_sales_cost"]:,.2f} | ต้นทุนอะไหล่ซ่อม: {agg["total_parts_cost"]:,.2f}')
            self.stdout.write(f'  - % กำไรงานซ่อม: {repair_profit_percent:,.2f}%')

