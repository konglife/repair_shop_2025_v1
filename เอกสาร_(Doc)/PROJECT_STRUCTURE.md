# โครงสร้างโปรเจคระบบร้านซ่อม

## 1. โครงสร้างของระบบ

ระบบประกอบด้วยแอปพลิเคชันหลัก ดังนี้:

### 1.1 Customers App
- จัดการข้อมูลลูกค้า
- โมเดลหลัก: `Customer`
- ความสัมพันธ์: เชื่อมโยงกับ `RepairJob` และ `Sale`

### 1.2 Inventory App
- จัดการสินค้า คลังสินค้า และการสั่งซื้อ
- โมเดลหลัก: `Product`, `Supplier`, `Stock`, `Purchase`
- ความสัมพันธ์:
    - `Product` มีเฉพาะราคาขาย (selling_price)
    - `Purchase` เก็บราคาซื้อ (price) ของแต่ละล็อต
    - `Stock` มีฟิลด์ average_cost (ราคาทุนเฉลี่ย) ซึ่งคำนวณแบบ Moving Average ทุกครั้งที่มีการรับสินค้าเข้า (Purchase ที่ status = Received)
    - **ไม่มีโมเดล ProductSupplier อีกต่อไป**
- หมายเหตุ: ราคาทุนเฉลี่ย (average_cost) จะอัปเดตอัตโนมัติใน Stock ตามประวัติการรับสินค้าเข้า

### 1.3 Repairs App
- จัดการงานซ่อมและชิ้นส่วนที่ใช้
- โมเดลหลัก: `RepairJob`, `UsedPart`
- ความสัมพันธ์: ใช้ข้อมูลลูกค้าและสินค้า

### 1.4 Sales App
- จัดการการขายสินค้า
- โมเดลหลัก: `Sale`, `SaleItem`
- ความสัมพันธ์: เชื่อมโยงกับสินค้าและลูกค้า

### 1.5 Dashboard App (กำลังพัฒนา)
- สรุปข้อมูลและวิเคราะห์
- โมเดลหลัก: `DailySummary`, `MonthlySummary`, `ProductStatistics`, `CustomerInsights`

## 2. หมายเหตุสำคัญ
- ระบบไม่มีการเก็บราคาซื้อแยกตาม Supplier อีกต่อไป ราคาซื้อจะถูกบันทึกในแต่ละ Purchase เท่านั้น
- average_cost ใน Stock จะสะท้อนต้นทุนเฉลี่ยล่าสุดของสินค้าแต่ละรายการ

## 3. ไฟล์สำคัญในระบบ

- **โมเดลหลัก**: 
  - `inventory/models.py`
  - `repairs/models.py`
  - `sales/models.py`
  - `customers/models.py`

- **ฟังก์ชันคำนวณ**: 
  - `repairs/utils/cost_calculation.py`

- **Signals**: 
  - `repairs/signals.py`
  - `inventory/signals.py`

- **เอกสารโปรเจค**:
  - `PROJECT_STRUCTURE.md` (ไฟล์นี้)
  - `DASHBOARD_DEVELOPMENT_PLAN.md`
