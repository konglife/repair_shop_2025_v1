from decimal import Decimal


def calculate_historical_weighted_average_cost(product):
    """
    คำนวณต้นทุนเฉลี่ยถ่วงน้ำหนักของสินค้าจากรายการซื้อทั้งหมดที่สถานะเป็น 'RECEIVED'
    (Historical Weighted Average)
    
    Args:
        product: instance ของ Product model
        
    Returns:
        Decimal: ค่าเฉลี่ยของต้นทุนซื้อ (weighted average cost)
    """
    from inventory.models import Purchase
    
    purchases = Purchase.objects.filter(
        product=product,
        status='RECEIVED'
    )
    
    if not purchases.exists():
        return Decimal('0.00')
        
    total_value = sum(
        purchase.quantity * (purchase.price or Decimal('0.00'))
        for purchase in purchases
    )
    total_quantity = sum(purchase.quantity for purchase in purchases)
    
    if total_quantity == 0:
        return Decimal('0.00')
        
    return total_value / total_quantity

def update_repair_job_costs(repair_job):
    """
    อัปเดตต้นทุนจริงในงานซ่อม
    
    Args:
        repair_job: instance ของ RepairJob model
    """
    parts = repair_job.used_parts.all()
    
    # คำนวณต้นทุนรวมทั้งหมดของชิ้นส่วน
    total_parts_cost = sum(part.quantity * part.cost_price_per_unit for part in parts)
    
    # อัปเดตค่าต้นทุนชิ้นส่วนในโมเดล
    repair_job.parts_cost_total = total_parts_cost
    
    # บันทึกเฉพาะฟิลด์ที่เกี่ยวข้อง
    repair_job.save(update_fields=['parts_cost_total', 'total_amount'])
