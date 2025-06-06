# dashboard/views.py
from django.shortcuts import render
from .models import DailySummary
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from sales.models import Sale
from repairs.models import RepairJob
from .utils import calculate_daily_sales_metrics, get_best_selling_products, calculate_comparison_with_previous, get_monthly_summary_live
# @login_required # เอา login_required ออกก่อน เพื่อให้ทดสอบได้ง่าย
def dashboard_home(request):
    today_date = timezone.now().date()
    yesterday_date = today_date - timedelta(days=1)

    # --- ดึงข้อมูลสรุปของเมื่อวาน (ถ้ามี) --- 
    yesterday_summary = DailySummary.objects.filter(date=yesterday_date).first()

    # --- คำนวณข้อมูลสดของวันนี้ (Live Calculation) โดยใช้ utils ---
    today_live_data = calculate_daily_sales_metrics(today_date)

    # --- ดึงข้อมูลสินค้าขายดี ---
    best_selling_products = get_best_selling_products(date=today_date, limit=5)

    # --- แปลง top_repairs (JSON string) เป็น Python object สำหรับ summary (เมื่อวาน) ---
    import json
    if yesterday_summary:
        if yesterday_summary.top_repairs:
            try:
                yesterday_summary.top_repairs = json.loads(yesterday_summary.top_repairs)
            except Exception:
                yesterday_summary.top_repairs = []
        else:
            yesterday_summary.top_repairs = []

    # --- เปรียบเทียบข้อมูลวันนี้กับเมื่อวาน ---
    if yesterday_summary:
        comparison_data = calculate_comparison_with_previous(today_live_data, yesterday_summary)
    else:
        comparison_data = None

    # --- เตรียมข้อมูลสำหรับกราฟ (Phase 3) ---
    days_to_show = 7
    start_date_chart = today_date - timedelta(days=days_to_show - 1)

    # ดึงข้อมูล DailySummary ย้อนหลัง
    summary_data = DailySummary.objects.filter(
        date__gte=start_date_chart, 
        date__lte=today_date  # รวมข้อมูลของวันนี้ด้วย (ถ้ามี)
    ).order_by('date')
    
    # สร้าง Dictionary เพื่อให้เข้าถึงข้อมูลตามวันได้ง่าย (เผื่อบางวันไม่มีข้อมูล)
    summary_dict = {summary.date: summary for summary in summary_data}

    chart_labels = []
    chart_revenue_data = []
    chart_profit_data = []
    chart_sales_count_data = []
    chart_repairs_count_data = []

    # วนลูปตามช่วงวันที่เพื่อให้แน่ใจว่ามีครบทุกวันในกราฟ
    for i in range(days_to_show):
        current_chart_date = start_date_chart + timedelta(days=i)
        chart_labels.append(current_chart_date.strftime("%d %b")) # Format วันที่ เช่น "09 Apr"

        summary_for_day = summary_dict.get(current_chart_date)
        if summary_for_day:
            chart_revenue_data.append(float(summary_for_day.total_revenue))
            chart_profit_data.append(float(summary_for_day.total_profit))  # แก้จาก total_repairs_profit เป็น total_profit
            chart_sales_count_data.append(summary_for_day.sales_count)
            chart_repairs_count_data.append(summary_for_day.repairs_completed_count)
        else:
            # ถ้าวันนั้นไม่มีข้อมูล ให้ใส่ 0 หรือ null (เลือก 0 ก่อน ง่ายกว่า)
            chart_revenue_data.append(0)
            chart_profit_data.append(0)
            chart_sales_count_data.append(0)
            chart_repairs_count_data.append(0)
            
    # print(f"Chart Labels: {chart_labels}") # เอาออก
    # print(f"Chart Revenue Data: {chart_revenue_data}") # เอาออก
    # print(f"Chart Profit Data: {chart_profit_data}") # เอาออก
    # print(f"Chart Sales Count Data: {chart_sales_count_data}") # เอาออก
    # print(f"Chart Repairs Count Data: {chart_repairs_count_data}") # เอาออก

    # --- เตรียมข้อมูลสำหรับกราฟรายเดือน ---
    monthly_summary = get_monthly_summary_live()
    from datetime import datetime
    monthly_chart_labels = [datetime.strptime(month, "%Y-%m").strftime("%b") for month in monthly_summary.keys()]
    monthly_chart_revenue_data = [float(summary['total_revenue']) for summary in monthly_summary.values()]
    monthly_chart_profit_data = [float(summary['total_profit']) for summary in monthly_summary.values()]
    monthly_chart_sales_count_data = [summary['sales_count'] for summary in monthly_summary.values()]
    monthly_chart_repairs_count_data = [summary['repairs_completed_count'] for summary in monthly_summary.values()]

    # --- ข้อมูลสรุปรายเดือนแบบ Live (real-time aggregate จาก DailySummary)
    this_month = timezone.now().strftime('%Y-%m')
    monthly_summary_live = monthly_summary.get(this_month, None)

    context = {
        'yesterday_summary': yesterday_summary,
        'today_live_data': today_live_data,
        'monthly_summary_live': monthly_summary_live,  # ใช้ live summary สำหรับการ์ดเดือนนี้
        'is_monthly_live': True,  # สำหรับ template แสดงป้าย Live
        'is_yesterday_batch': True,  # สำหรับ template แสดงป้าย Batch

        'best_selling_products': best_selling_products,
        'comparison_data': comparison_data,
        'current_date': timezone.now(), # ใช้ datetime object
        # ข้อมูลสำหรับกราฟ
        'chart_labels': chart_labels,
        'chart_revenue_data': chart_revenue_data,
        'chart_profit_data': chart_profit_data,
        'chart_sales_count_data': chart_sales_count_data,
        'chart_repairs_count_data': chart_repairs_count_data,
        # ข้อมูลสำหรับกราฟรายเดือน
        'monthly_chart_labels': monthly_chart_labels,
        'monthly_chart_revenue_data': monthly_chart_revenue_data,
        'monthly_chart_profit_data': monthly_chart_profit_data,
        'monthly_chart_sales_count_data': monthly_chart_sales_count_data,
        'monthly_chart_repairs_count_data': monthly_chart_repairs_count_data,
    }
    return render(request, 'dashboard/home.html', context) # ตรวจสอบว่า render template ถูกต้อง