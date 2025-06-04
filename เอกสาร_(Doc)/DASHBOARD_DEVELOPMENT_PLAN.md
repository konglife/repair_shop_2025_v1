# แผนการพัฒนา Dashboard สำหรับระบบร้านซ่อม

## 1. ภาพรวมและวัตถุประสงค์

Dashboard นี้มีวัตถุประสงค์เพื่อ:
- แสดงข้อมูลสรุปทางธุรกิจสำหรับร้านซ่อม
- แสดงข้อมูลวิเคราะห์เพื่อสนับสนุนการตัดสินใจ
- ติดตามประสิทธิภาพของงานซ่อมและการขาย
- เตือนเมื่อสินค้าใกล้หมดหรือต้องสั่งซื้อเพิ่ม
- สร้างรายงานธุรกิจในรูปแบบ PDF และ Excel
- ตรวจสอบงานซ่อมค้างนานและการชำระเงิน

## 2. โมเดลหลักของ Dashboard

### 2.1 SummaryBase (Abstract Model)
```python
class SummaryBase(models.Model):
    date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
```

### 2.2 DailySummary (ปรับปรุงแล้ว)
```python
class DailySummary(SummaryBase):
    date = models.DateField(unique=True)
    
    # ข้อมูลรายรับ
    total_sales_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_repairs_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0, editable=False)
    
    # ข้อมูลต้นทุนและกำไร
    total_sales_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0) # ต้นทุนอะไหล่ซ่อม
    total_labor_charge = models.DecimalField(max_digits=12, decimal_places=2, default=0) # ค่าแรงซ่อม
    total_sales_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_repairs_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # จำนวนรายการ
    sales_count = models.IntegerField(default=0)
    repairs_completed_count = models.IntegerField(default=0)
    
    # ข้อมูลลูกค้า
    active_customers_count = models.PositiveIntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    
    # ข้อมูลเปรียบเทียบ
    total_revenue_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_profit_change = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # สินค้าขายดี
    top_selling_product_id = models.IntegerField(null=True, blank=True)
    top_selling_product_name = models.CharField(max_length=100, blank=True)
```

### 2.3 MonthlySummary
```python
class MonthlySummary(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    repair_jobs_count = models.IntegerField(default=0)
    sales_count = models.IntegerField(default=0)
    revenue_repair = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    revenue_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_repair = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cost_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    new_customers = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('year', 'month')
```

### 2.4 ProductStatistics
```python
class ProductStatistics(models.Model):
    product = models.OneToOneField('inventory.Product', on_delete=models.CASCADE)
    total_sales_quantity = models.IntegerField(default=0)
    total_repair_usage = models.IntegerField(default=0)
    last_sale_date = models.DateField(null=True, blank=True)
    last_repair_usage_date = models.DateField(null=True, blank=True)
    total_sales_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_profit_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)
```

### 2.5 CustomerInsights
```python
class CustomerInsights(models.Model):
    customer = models.OneToOneField('customers.Customer', on_delete=models.CASCADE)
    total_repair_jobs = models.IntegerField(default=0)
    total_sales = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    avg_repair_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    first_visit_date = models.DateField(null=True, blank=True)
    latest_visit_date = models.DateField(null=True, blank=True)
    visit_frequency_days = models.IntegerField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
```

### 2.6 InventoryAlert
```python
class InventoryAlert(models.Model):
    ALERT_TYPES = [
        ('LOW_STOCK', 'สินค้าใกล้หมด'),
        ('OUT_OF_STOCK', 'สินค้าหมด'),
        ('REORDER', 'ควรสั่งซื้อเพิ่ม'),
    ]
    
    product = models.ForeignKey('inventory.Product', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
```

### 2.7 RepairAlert (เพิ่มเติม)
```python
class RepairAlert(models.Model):
    ALERT_TYPES = [
        ('OVERDUE', 'งานซ่อมค้างนาน'),
        ('PENDING_PAYMENT', 'รอการชำระเงิน'),
        ('PARTS_WAITING', 'รออะไหล่'),
    ]
    
    repair_job = models.ForeignKey('repairs.RepairJob', on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    days_pending = models.IntegerField(default=0)  # จำนวนวันที่ค้าง
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
```

## 3. กลไกการอัปเดตข้อมูล

### 3.1 Signal-based Updates

#### 3.1.1 RepairJob Signals
```python
@receiver(post_save, sender=RepairJob)
def update_dashboard_on_repair_job_save(sender, instance, created, **kwargs):
    # อัปเดต DailySummary
    daily_summary, _ = DailySummary.objects.get_or_create(date=instance.repair_date.date())
    
    # อัปเดต CustomerInsights
    customer_insights, _ = CustomerInsights.objects.get_or_create(customer=instance.customer)
    
    # คำนวณและอัปเดตข้อมูล...
```

#### 3.1.2 Sale Signals
```python
@receiver(post_save, sender=Sale)
def update_dashboard_on_sale_save(sender, instance, created, **kwargs):
    # อัปเดต DailySummary
    daily_summary, _ = DailySummary.objects.get_or_create(date=instance.sale_date.date())
    
    # อัปเดต CustomerInsights ถ้ามีลูกค้าเกี่ยวข้อง
    if instance.customer:
        customer_insights, _ = CustomerInsights.objects.get_or_create(customer=instance.customer)
    
    # คำนวณและอัปเดตข้อมูล...
```

#### 3.1.3 Stock Signals
```python
@receiver(post_save, sender=Stock)
def check_inventory_alerts(sender, instance, **kwargs):
    # ตรวจสอบสถานะสินค้าคงเหลือ
    if instance.current_stock <= 0:
        InventoryAlert.objects.get_or_create(
            product=instance.product,
            alert_type='OUT_OF_STOCK',
            resolved=False,
            defaults={'message': f'สินค้า {instance.product.name} หมดสต็อก'}
        )
    elif instance.current_stock <= instance.min_stock:
        InventoryAlert.objects.get_or_create(
            product=instance.product,
            alert_type='LOW_STOCK',
            resolved=False,
            defaults={'message': f'สินค้า {instance.product.name} เหลือน้อย (เหลือ {instance.current_stock})'}
        )
```

#### 3.1.4 RepairJob Signals (เพิ่มเติม)
```python
@receiver(post_save, sender=RepairJob)
def check_repair_alerts(sender, instance, **kwargs):
    # ถ้างานซ่อมยังไม่เสร็จและค้างมานานเกิน 7 วัน
    if instance.status == 'IN_PROGRESS':
        repair_date = instance.repair_date.date()
        today = date.today()
        days_pending = (today - repair_date).days
        
        if days_pending >= 7:
            RepairAlert.objects.get_or_create(
                repair_job=instance,
                alert_type='OVERDUE',
                resolved=False,
                defaults={
                    'message': f'งานซ่อม {instance.job_name} ค้างมา {days_pending} วันแล้ว',
                    'days_pending': days_pending
                }
            )
            
    # ถ้างานซ่อมเสร็จแล้วแต่ยังไม่ได้ชำระเงิน
    elif instance.status == 'COMPLETED' and instance.payment == 'UNPAID':
        RepairAlert.objects.get_or_create(
            repair_job=instance,
            alert_type='PENDING_PAYMENT',
            resolved=False,
            defaults={'message': f'งานซ่อม {instance.job_name} เสร็จแล้วแต่ยังไม่ได้ชำระเงิน'}
        )
```

### 3.2 Management Commands

#### 3.2.1 generate_daily_summary.py
```python
class Command(BaseCommand):
    help = 'สร้างหรืออัปเดตข้อมูลสรุปรายวัน'
    
    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='วันที่ต้องการสร้างข้อมูลสรุป (YYYY-MM-DD)')
    
    def handle(self, *args, **kwargs):
        date_str = kwargs.get('date')
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today() - timedelta(days=1)  # เมื่อวาน
        
        # สร้างหรือดึงข้อมูล DailySummary
        summary, created = DailySummary.objects.get_or_create(date=target_date)
        
        # คำนวณข้อมูลสรุปจาก RepairJob
        repair_jobs = RepairJob.objects.filter(repair_date__date=target_date)
        summary.repair_jobs_count = repair_jobs.count()
        summary.revenue_repair = repair_jobs.aggregate(Sum('total_charge'))['total_charge__sum'] or 0
        summary.cost_repair = repair_jobs.aggregate(Sum('parts_cost_total'))['parts_cost_total__sum'] or 0
        
        # คำนวณข้อมูลสรุปจาก Sale
        sales = Sale.objects.filter(created_at__date=target_date)
        summary.sales_count = sales.count()
        summary.revenue_sales = sales.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        # คำนวณ cost_sales ตาม logic ของธุรกิจ
        
        # คำนวณกำไรรวม
        summary.profit = (summary.revenue_repair + summary.revenue_sales) - (summary.cost_repair + summary.cost_sales)
        
        # ลูกค้าใหม่
        customers_with_first_purchase = Customer.objects.filter(
            models.Q(repair_jobs__repair_date__date=target_date) | models.Q(sales__created_at__date=target_date),
            created_at__date=target_date
        ).distinct()
        summary.new_customers = customers_with_first_purchase.count()
        
        summary.save()
        
        self.stdout.write(self.style.SUCCESS(f'สร้างข้อมูลสรุปรายวันสำหรับ {target_date} เรียบร้อยแล้ว'))
```

#### 3.2.2 generate_monthly_summary.py
```python
class Command(BaseCommand):
    help = 'สร้างหรืออัปเดตข้อมูลสรุปรายเดือน'
    
    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='ปีที่ต้องการสร้างข้อมูลสรุป')
        parser.add_argument('--month', type=int, help='เดือนที่ต้องการสร้างข้อมูลสรุป (1-12)')
    
    def handle(self, *args, **kwargs):
        year = kwargs.get('year')
        month = kwargs.get('month')
        
        if not year or not month:
            # ถ้าไม่ระบุ ใช้เดือนก่อนหน้า
            today = date.today()
            if today.month == 1:
                year = today.year - 1
                month = 12
            else:
                year = today.year
                month = today.month - 1
        
        # สร้างหรือดึงข้อมูล MonthlySummary
        summary, created = MonthlySummary.objects.get_or_create(year=year, month=month)
        
        # รวมข้อมูลจาก DailySummary
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        daily_summaries = DailySummary.objects.filter(date__gte=start_date, date__lte=end_date)
        
        # คำนวณสรุปรายเดือน
        summary.repair_jobs_count = daily_summaries.aggregate(Sum('repair_jobs_count'))['repair_jobs_count__sum'] or 0
        summary.sales_count = daily_summaries.aggregate(Sum('sales_count'))['sales_count__sum'] or 0
        summary.revenue_repair = daily_summaries.aggregate(Sum('revenue_repair'))['revenue_repair__sum'] or 0
        summary.revenue_sales = daily_summaries.aggregate(Sum('revenue_sales'))['revenue_sales__sum'] or 0
        summary.cost_repair = daily_summaries.aggregate(Sum('cost_repair'))['cost_repair__sum'] or 0
        summary.cost_sales = daily_summaries.aggregate(Sum('cost_sales'))['cost_sales__sum'] or 0
        summary.profit = daily_summaries.aggregate(Sum('profit'))['profit__sum'] or 0
        summary.new_customers = daily_summaries.aggregate(Sum('new_customers'))['new_customers__sum'] or 0
        
        summary.save()
        
        self.stdout.write(self.style.SUCCESS(f'สร้างข้อมูลสรุปรายเดือนสำหรับ {month}/{year} เรียบร้อยแล้ว'))
```

## 4. การดึงและแสดงข้อมูล

### 4.1 Views สำหรับ Dashboard

```python
def dashboard_home(request):
    # ข้อมูลสรุปล่าสุด
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # สรุปรายวัน
    try:
        daily_summary = DailySummary.objects.get(date=yesterday)
    except DailySummary.DoesNotExist:
        daily_summary = None
    
    # สรุปรายเดือน
    current_month = today.month
    current_year = today.year
    
    try:
        if current_month == 1:
            monthly_summary = MonthlySummary.objects.get(year=current_year-1, month=12)
        else:
            monthly_summary = MonthlySummary.objects.get(year=current_year, month=current_month-1)
    except MonthlySummary.DoesNotExist:
        monthly_summary = None
    
    # การแจ้งเตือนคลังสินค้า
    inventory_alerts = InventoryAlert.objects.filter(resolved=False).order_by('-created_at')
    
    # การแจ้งเตือนงานซ่อม
    repair_alerts = RepairAlert.objects.filter(resolved=False).order_by('-created_at')
    
    # งานซ่อมล่าสุด
    recent_repair_jobs = RepairJob.objects.order_by('-repair_date')[:5]
    
    # สินค้าขายดี
    top_products = ProductStatistics.objects.order_by('-total_sales_quantity')[:5]
    
    context = {
        'daily_summary': daily_summary,
        'monthly_summary': monthly_summary,
        'inventory_alerts': inventory_alerts,
        'repair_alerts': repair_alerts,
        'recent_repair_jobs': recent_repair_jobs,
        'top_products': top_products,
    }
    
    return render(request, 'dashboard/home.html', context)
```

### 4.2 การคำนวณและ Cache ข้อมูล

```python
def get_profit_trend(days=30):
    """ดึงข้อมูลแนวโน้มกำไรย้อนหลัง X วัน พร้อม cache"""
    cache_key = f'profit_trend_{days}'
    cached_data = cache.get(cache_key)
    
    if cached_data is not None:
        return cached_data
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    summaries = DailySummary.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    result = [
        {
            'date': summary.date.strftime('%Y-%m-%d'),
            'profit': float(summary.profit),
            'revenue': float(summary.revenue_repair + summary.revenue_sales),
            'cost': float(summary.cost_repair + summary.cost_sales),
        }
        for summary in summaries
    ]
    
    # Cache ข้อมูล (หมดอายุใน 1 ชั่วโมง)
    cache.set(cache_key, result, 60*60)
    
    return result
```

### 4.3 การส่งออกรายงาน PDF และ Excel (เพิ่มเติม)

```python
def generate_daily_report_pdf(request, date=None):
    """สร้างรายงานสรุปรายวันเป็น PDF"""
    if date is None:
        # ใช้วันเมื่อวานเป็นค่าเริ่มต้น
        date = timezone.now().date() - timedelta(days=1)
    
    # ดึงข้อมูล DailySummary
    try:
        summary = DailySummary.objects.get(date=date)
    except DailySummary.DoesNotExist:
        return HttpResponse("ไม่พบข้อมูลสรุปรายวันสำหรับวันที่ระบุ", status=404)
    
    # ดึงข้อมูลการขายและงานซ่อมของวันนั้น
    sales = Sale.objects.filter(sale_date__date=date)
    repairs = RepairJob.objects.filter(repair_date__date=date)
    
    # สร้าง context สำหรับ template PDF
    context = {
        'summary': summary,
        'sales': sales,
        'repairs': repairs,
        'generated_at': timezone.now(),
    }
    
    # สร้าง HTML จาก template
    template = get_template('dashboard/reports/daily_report_pdf.html')
    html = template.render(context)
    
    # สร้าง PDF จาก HTML (ใช้ wkhtmltopdf)
    pdf = pdfkit.from_string(html, False)
    
    # ส่ง PDF กลับให้ user
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="daily_report_{date}.pdf"'
    
    return response

def generate_monthly_report_excel(request, year=None, month=None):
    """สร้างรายงานสรุปรายเดือนเป็น Excel"""
    if year is None or month is None:
        # ใช้เดือนปัจจุบัน
        today = timezone.now().date()
        year = today.year
        month = today.month
    
    # ดึงข้อมูล MonthlySummary
    try:
        summary = MonthlySummary.objects.get(year=year, month=month)
    except MonthlySummary.DoesNotExist:
        return HttpResponse("ไม่พบข้อมูลสรุปรายเดือนสำหรับเดือนที่ระบุ", status=404)
    
    # ดึงข้อมูล DailySummary ของเดือนนั้น
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    daily_summaries = DailySummary.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # สร้างไฟล์ Excel
    wb = Workbook()
    ws = wb.active
    ws.title = f"สรุปเดือน {month}/{year}"
    
    # เพิ่ม header
    headers = ["วันที่", "รายรับการขาย", "รายรับงานซ่อม", "รายรับรวม", 
               "ต้นทุนการขาย", "กำไรรวม", "จำนวนขาย", "จำนวนซ่อม"]
    ws.append(headers)
    
    # เพิ่มข้อมูลรายวัน
    for summary in daily_summaries:
        ws.append([
            summary.date.strftime('%Y-%m-%d'),
            float(summary.total_sales_revenue),
            float(summary.total_repairs_revenue),
            float(summary.total_revenue),
            float(summary.total_sales_cost),
            float(summary.total_profit),
            summary.sales_count,
            summary.repairs_completed_count
        ])
    
    # สรุปท้ายตาราง
    ws.append([])
    ws.append(["รวมทั้งเดือน", 
              float(summary.total_sales_revenue),
              float(summary.total_repairs_revenue),
              float(summary.total_revenue),
              float(summary.total_sales_cost),
              float(summary.total_profit),
              summary.sales_count,
              summary.repairs_completed_count])
    
    # จัดรูปแบบ
    for col in range(2, 7):
        for row in range(2, ws.max_row + 1):
            ws.cell(row=row, column=col).number_format = '#,##0.00'
    
    # บันทึกไฟล์
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=monthly_report_{year}_{month}.xlsx'
    wb.save(response)
    
    return response
```

## 5. การปรับแต่งประสิทธิภาพ (SQLite3)

### 5.1 การสร้าง Indexes

```python
# ตัวอย่าง Migration สำหรับสร้าง index

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        # สร้าง index สำหรับการค้นหาตามวันที่
        migrations.AddIndex(
            model_name='dailysummary',
            index=models.Index(fields=['date'], name='idx_daily_summary_date'),
        ),
        # สร้าง index สำหรับการค้นหาตามปี/เดือน
        migrations.AddIndex(
            model_name='monthlysummary',
            index=models.Index(fields=['year', 'month'], name='idx_monthly_summary_year_month'),
        ),
        # สร้าง index สำหรับการค้นหาการแจ้งเตือนที่ยังไม่แก้ไข
        migrations.AddIndex(
            model_name='inventoryalert',
            index=models.Index(fields=['resolved', 'created_at'], name='idx_inventory_alert_resolved_date'),
        ),
    ]
```

### 5.2 Denormalization

การเก็บข้อมูลที่คำนวณไว้แล้วใน ProductStatistics และ CustomerInsights เป็นการทำ denormalization เพื่อลดการ JOIN และเพิ่มประสิทธิภาพการคิวรี

### 5.3 การดูแลฐานข้อมูล

#### 5.3.1 วิธีการทำ VACUUM

```python
# Management command สำหรับทำ VACUUM
class Command(BaseCommand):
    help = 'ทำความสะอาดฐานข้อมูล SQLite ด้วยคำสั่ง VACUUM'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('เริ่มทำ VACUUM ฐานข้อมูล...')
        
        cursor = connection.cursor()
        cursor.execute('VACUUM;')
        
        self.stdout.write(self.style.SUCCESS('ทำ VACUUM ฐานข้อมูลเรียบร้อยแล้ว'))
```

## 6. การทดสอบ

### 6.1 Unit Tests

```python
class DashboardModelTests(TestCase):
    def setUp(self):
        # สร้างข้อมูลทดสอบ
        self.customer = Customer.objects.create(name="ลูกค้าทดสอบ")
        self.product = Product.objects.create(
            name="สินค้าทดสอบ", 
            selling_price=100.00
        )
        
        # สร้างข้อมูล Stock
        Stock.objects.create(
            product=self.product,
            min_stock=5,
            current_stock=10
        )
        
        # สร้างข้อมูล RepairJob
        self.repair_job = RepairJob.objects.create(
            job_name="งานซ่อมทดสอบ",
            customer=self.customer,
            repair_date=timezone.now(),
            description="รายละเอียดทดสอบ",
            labor_charge=200.00,
            parts_selling_total=0,
            parts_cost_total=0,
            total_charge=200.00,
            status="COMPLETED"
        )
    
    def test_daily_summary_creation(self):
        # เรียกใช้คำสั่งสร้างข้อมูลสรุปรายวัน
        call_command('generate_daily_summary')
        
        # ตรวจสอบว่ามีข้อมูลสรุปรายวันถูกสร้างขึ้น
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        self.assertTrue(DailySummary.objects.filter(date=yesterday).exists())
        
        summary = DailySummary.objects.get(date=yesterday)
        self.assertEqual(summary.repair_jobs_count, 1)
        self.assertEqual(summary.revenue_repair, 200.00)
```

### 6.2 Integration Tests

```python
class DashboardIntegrationTests(TestCase):
    def setUp(self):
        # สร้างข้อมูลทดสอบเหมือนใน Unit Tests
        ...
        
    def test_stock_alert_creation(self):
        # ทดสอบว่าเมื่อสินค้าเหลือน้อย จะมีการสร้างการแจ้งเตือน
        stock = Stock.objects.get(product=self.product)
        stock.current_stock = 3  # น้อยกว่า min_stock
        stock.save()
        
        # ตรวจสอบว่ามีการแจ้งเตือนถูกสร้างขึ้น
        self.assertTrue(InventoryAlert.objects.filter(
            product=self.product,
            alert_type='LOW_STOCK',
            resolved=False
        ).exists())
    
    def test_dashboard_view(self):
        # เรียกใช้คำสั่งสร้างข้อมูลสรุป
        call_command('generate_daily_summary')
        
        # ทดสอบการเข้าถึง dashboard view
        response = self.client.get(reverse('dashboard:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/home.html')
        
        # ตรวจสอบว่ามีข้อมูลที่ต้องการในหน้า
        self.assertContains(response, 'งานซ่อมทดสอบ')
```

## 7. การดำเนินการต่อไป

### 7.1 ขั้นตอนการพัฒนา

1. สร้างแอป Dashboard และโมเดลพื้นฐาน
2. พัฒนา management commands สำหรับสร้างข้อมูลสรุป
3. เพิ่ม signals เพื่ออัปเดตข้อมูลอัตโนมัติ
4. พัฒนาหน้า dashboard หลัก
5. เพิ่มการแสดงกราฟและการวิเคราะห์
6. พัฒนาระบบรายงาน PDF และ Excel
7. พัฒนาระบบแจ้งเตือนที่ครอบคลุม
8. ปรับแต่งประสิทธิภาพและทำการทดสอบ

### 7.2 ความเสี่ยงและการแก้ไข

1. **ประสิทธิภาพของ SQLite3**: เมื่อข้อมูลมากขึ้น อาจกำหนดการเก็บข้อมูลเฉพาะช่วงเวลาล่าสุด
2. **ความถูกต้องของข้อมูล**: ตรวจสอบความสอดคล้องระหว่างข้อมูลต้นทางและข้อมูลสรุปเป็นประจำ
3. **การใช้งานเครื่อง**: หากระบบทำงานช้าอาจต้องปรับความถี่ในการคำนวณข้อมูลสรุป
4. **ความผิดพลาดในการสร้างรายงาน**: ตรวจสอบความถูกต้องของรายงานอย่างสม่ำเสมอ

### 7.3 ไลบรารีที่แนะนำสำหรับรายงาน

1. **สำหรับ PDF**:
   - `django-pdfkit`: ใช้ wkhtmltopdf เพื่อแปลง HTML เป็น PDF คุณภาพสูง
   - `reportlab`: ไลบรารีมาตรฐานสำหรับสร้าง PDF โดยตรง
   - `xhtml2pdf`: แปลง HTML/CSS เป็น PDF

2. **สำหรับ Excel**:
   - `openpyxl`: ไลบรารีที่ใช้งานง่ายสำหรับสร้างไฟล์ Excel
   - `xlsxwriter`: ตัวเลือกที่มีประสิทธิภาพสูงสำหรับสร้าง Excel ที่ซับซ้อน
``` 
</rewritten_file>