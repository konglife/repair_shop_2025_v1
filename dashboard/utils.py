from django.db.models import Sum, Count, F, Q, Avg, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

from sales.models import Sale, SaleItem
from repairs.models import RepairJob
from inventory.models import Product
from dashboard.models import DailySummary, MonthlySummary

def calculate_daily_sales_metrics(date):
    """
    คำนวณยอดขายและกำไรแบบ real-time สำหรับวันที่ระบุ
    
    Args:
        date (date): วันที่ต้องการคำนวณข้อมูล
        
    Returns:
        dict: ข้อมูลสรุปยอดขายและกำไรของวันที่ระบุ
    """
    # 1. ยอดขายสินค้า
    sales_data = Sale.objects.filter(
        sale_date__date=date,
        payment='PAID'
    ).aggregate(
        total_sales=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal('0.00')),
        count=Coalesce(Count('id', output_field=IntegerField()), 0)
    )
    
    # 2. คำนวณต้นทุนการขายสินค้า
    sales_items = SaleItem.objects.filter(
        sale__sale_date__date=date,
        sale__payment='PAID'
    )
    
    total_sales_cost = Decimal('0.00')
    
    for item in sales_items:
        if item.product:
            # TODO: ใช้ average_cost จาก Stock แทน ProductSupplier
            avg_cost = item.product.stocks.first().average_cost if item.product.stocks.exists() else Decimal('0.00')
            total_sales_cost += item.quantity * avg_cost
    
    # คำนวณกำไรจากการขายสินค้า
    total_sales_profit = sales_data['total_sales'] - total_sales_cost
    
    # 3. งานซ่อม
    repairs_data = RepairJob.objects.filter(
        repair_date__date=date,
        status='COMPLETED'
    ).aggregate(
        total_repairs_revenue=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal('0.00')),
        total_parts_cost=Coalesce(Sum('parts_cost_total', output_field=DecimalField()), Decimal('0.00')),
        repairs_completed_count=Coalesce(Count('id', output_field=IntegerField()), 0),
    )
    
    # คำนวณกำไรจากงานซ่อม
    total_repairs_profit = repairs_data['total_repairs_revenue'] - repairs_data['total_parts_cost']
    # % กำไรงานซ่อม
    repair_profit_percent = (total_repairs_profit / repairs_data['total_repairs_revenue'] * 100) if repairs_data['total_repairs_revenue'] else 0
    # Top 5 งานซ่อมที่ทำบ่อย/ทำเงินสูงสุด
    top_repairs_qs = RepairJob.objects.filter(repair_date__date=date, status='COMPLETED')\
        .values('job_name')\
        .annotate(count=Coalesce(Count('id', output_field=IntegerField()), 0), amount=Coalesce(Sum('total_amount', output_field=DecimalField()), Decimal('0.00')))\
        .order_by('-amount', '-count')[:5]
    top_repairs = [
        {'name': r['job_name'], 'count': r['count'], 'amount': r['amount']} for r in top_repairs_qs
    ]
    # 4. รวมรายรับและกำไรทั้งหมด
    total_revenue = sales_data['total_sales'] + repairs_data['total_repairs_revenue']
    total_profit = total_sales_profit + total_repairs_profit
    
    # สร้าง dictionary เก็บข้อมูล
    metrics = {
        'date': date,
        'total_sales_revenue': sales_data['total_sales'],
        'total_sales_cost': total_sales_cost,
        'total_sales_profit': total_sales_profit,
        'sales_count': sales_data['count'],
        
        'total_repairs_revenue': repairs_data['total_repairs_revenue'],
        'total_parts_cost': repairs_data['total_parts_cost'],
        'total_repairs_profit': total_repairs_profit,
        'repair_profit_percent': repair_profit_percent,
        'repairs_completed_count': repairs_data['repairs_completed_count'],
        
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'top_repairs': top_repairs,
    }
    
    return metrics

def get_best_selling_products(date=None, limit=5, period_days=None):
    """
    ดึงข้อมูลสินค้าขายดี top 5 ตามวันที่หรือช่วงเวลาที่กำหนด
    
    Args:
        date (date, optional): วันที่ต้องการดูข้อมูล (ถ้าไม่ระบุจะใช้วันปัจจุบัน)
        limit (int, optional): จำนวนสินค้าที่ต้องการดึงข้อมูล (default: 5)
        period_days (int, optional): ช่วงเวลาย้อนหลังกี่วัน (ถ้าไม่ระบุจะใช้เฉพาะวันที่กำหนด)
        
    Returns:
        list: รายการสินค้าขายดีพร้อมข้อมูลการขาย
    """
    if date is None:
        date = timezone.now().date()
    
    if period_days:
        start_date = date - timedelta(days=period_days)
        date_filter = Q(sale__sale_date__date__gte=start_date) & Q(sale__sale_date__date__lte=date)
    else:
        date_filter = Q(sale__sale_date__date=date)
    
    # ดึงข้อมูลสินค้าขายดีตามจำนวนที่ขายได้ (quantity)
    best_selling_items = SaleItem.objects.filter(
        date_filter,
        sale__payment='PAID'
    ).values(
        'product'
    ).annotate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'), output_field=DecimalField()),
        sales_count=Count('sale', distinct=True)
    ).order_by('-total_quantity')[:limit]
    
    # เพิ่มข้อมูลรายละเอียดของสินค้า
    result = []
    for item in best_selling_items:
        product = Product.objects.filter(id=item['product']).first()
        if product:
            result.append({
                'product_id': product.id,
                'name': product.name,
                'total_quantity': item['total_quantity'],
                'total_revenue': item['total_revenue'],
                'sales_count': item['sales_count'],
            })
    
    return result

def calculate_comparison_with_previous(summary, previous_summary):
    """
    เปรียบเทียบข้อมูลกับข้อมูลก่อนหน้า เพื่อหาเปอร์เซ็นต์การเปลี่ยนแปลง
    
    Args:
        summary (DailySummary หรือ dict): ข้อมูลสรุปปัจจุบัน
        previous_summary (DailySummary หรือ dict): ข้อมูลสรุปก่อนหน้า
        
    Returns:
        dict: ข้อมูลเปรียบเทียบแสดงเปอร์เซ็นต์การเปลี่ยนแปลง
    """
    if not previous_summary:
        # ถ้าไม่มีข้อมูลเปรียบเทียบ ส่งค่า None หรือ 0
        return {
            'revenue_change': None,
            'revenue_change_percent': None,
            'profit_change': None,
            'profit_change_percent': None,
            'sales_count_change': None,
            'sales_count_change_percent': None,
            'repairs_count_change': None,
            'repairs_count_change_percent': None,
        }
    
    # ดึงข้อมูลจาก summary หรือ dictionary
    if isinstance(summary, DailySummary):
        current_revenue = summary.total_revenue
        current_profit = summary.total_profit
        current_sales_count = summary.sales_count
        current_repairs_count = summary.repairs_completed_count
    else:
        current_revenue = summary.get('total_revenue', 0)
        current_profit = summary.get('total_profit', 0)
        current_sales_count = summary.get('sales_count', 0)
        current_repairs_count = summary.get('repairs_completed_count', 0)
    
    # ดึงข้อมูลจาก previous_summary
    if isinstance(previous_summary, DailySummary):
        previous_revenue = previous_summary.total_revenue
        previous_profit = previous_summary.total_profit
        previous_sales_count = previous_summary.sales_count
        previous_repairs_count = previous_summary.repairs_completed_count
    else:
        previous_revenue = previous_summary.get('total_revenue', 0)
        previous_profit = previous_summary.get('total_profit', 0)
        previous_sales_count = previous_summary.get('sales_count', 0)
        previous_repairs_count = previous_summary.get('repairs_completed_count', 0)
    
    # คำนวณการเปลี่ยนแปลง
    revenue_change = current_revenue - previous_revenue
    profit_change = current_profit - previous_profit
    sales_count_change = current_sales_count - previous_sales_count
    repairs_count_change = current_repairs_count - previous_repairs_count
    
    # คำนวณเปอร์เซ็นต์การเปลี่ยนแปลง (ระวังกรณีหารด้วย 0)
    revenue_change_percent = (revenue_change / previous_revenue * 100) if previous_revenue else None
    profit_change_percent = (profit_change / previous_profit * 100) if previous_profit else None
    sales_count_change_percent = (sales_count_change / previous_sales_count * 100) if previous_sales_count else None
    repairs_count_change_percent = (repairs_count_change / previous_repairs_count * 100) if previous_repairs_count else None
    
    return {
        'revenue_change': revenue_change,
        'revenue_change_percent': revenue_change_percent,
        'profit_change': profit_change,
        'profit_change_percent': profit_change_percent,
        'sales_count_change': sales_count_change,
        'sales_count_change_percent': sales_count_change_percent,
        'repairs_count_change': repairs_count_change,
        'repairs_count_change_percent': repairs_count_change_percent,
    }


def get_monthly_summary_live(month=None, months_back=6):
    """
    สรุปข้อมูลรายเดือนแบบ live จาก DailySummary
    - ถ้า month (str: 'YYYY-MM') ระบุ จะคืน dict ของเดือนนั้น
    - ถ้าไม่ระบุ จะคืน dict ของหลายเดือนย้อนหลัง (key=month 'YYYY-MM')
    """
    from collections import OrderedDict
    from datetime import date
    today = timezone.now().date()
    summaries = OrderedDict()

    def month_range(dt):
        return dt.replace(day=1)

    if month:
        # สรุปเฉพาะเดือนที่ระบุ
        year, m = map(int, month.split('-'))
        start = date(year, m, 1)
        if m == 12:
            end = date(year+1, 1, 1)
        else:
            end = date(year, m+1, 1)
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
        agg['total_revenue'] = agg['total_sales_revenue'] + agg['total_repairs_revenue']
        agg['total_profit'] = agg['total_sales_profit'] + agg['total_repairs_profit']
        agg['month'] = month
        return agg
    else:
        # สรุปย้อนหลังหลายเดือน (default 6 เดือน) + รวมเดือนปัจจุบันเป็นเดือนแรก
        from collections import OrderedDict
        summaries = OrderedDict()
        today = timezone.now().date()
        months = []
        current_month = today.replace(day=1)
        months.append(current_month)
        for i in range(1, months_back):
            prev_month = (current_month - timedelta(days=1)).replace(day=1)
            months.append(prev_month)
            current_month = prev_month
        # วนลูปตาม months (เรียงจากปัจจุบัน -> ย้อนหลัง)
        for ref_month in months:
            month_str = ref_month.strftime('%Y-%m')
            year, m = ref_month.year, ref_month.month
            if m == 12:
                end = date(year+1, 1, 1)
            else:
                end = date(year, m+1, 1)
            qs = DailySummary.objects.filter(date__gte=ref_month, date__lt=end)
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
            agg['total_revenue'] = agg['total_sales_revenue'] + agg['total_repairs_revenue']
            agg['total_profit'] = agg['total_sales_profit'] + agg['total_repairs_profit']
            agg['month'] = month_str
            summaries[ref_month] = agg
        # สร้าง OrderedDict: key=month_str, value=agg
        return OrderedDict((v['month'], v) for k, v in summaries.items())