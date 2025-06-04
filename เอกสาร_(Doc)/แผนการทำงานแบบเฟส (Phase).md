ด้านล่างนี้คือการแบ่งงาน **พัฒนา Dashboard ระบบร้านซ่อม** โดยอ้างอิงจากแผนหลักใน `เอกสาร_(Doc)/DASHBOARD_DEVELOPMENT_PLAN.md` ออกเป็น **เฟส (Phase)**
โดยเรียงลำดับจากง่าย → ยาก พร้อมคำอธิบายแต่ละช่วง เหมาะกับมือใหม่ครับ 😊

---

## 🧩 แผนการทำงานแบบเฟส (Phase) - *ฉบับละเอียด*

*เน้นการใช้งาน Tailwind CSS เพื่อดีไซน์ที่ทันสมัยและตอบสนอง (Responsive)*
*อ้างอิง Model และกลไกจาก `DASHBOARD_DEVELOPMENT_PLAN.md`*

---

### 🚀 **Phase 1: เตรียมโครงสร้างและตั้งค่า Tailwind CSS**
**(สอดคล้องกับ แผนหลัก ส่วน 7.1 ขั้นตอนที่ 1, 4 เบื้องต้น)**
**เป้าหมาย:** เตรียมระบบให้พร้อมแสดง Dashboard ง่าย ๆ ด้วยโครงสร้างพื้นฐานและ Tailwind CSS

| รายการ | รายละเอียด |
|--------|-------------|
| ✅ 1.1 ตรวจสอบว่าแอป `dashboard` ถูกเพิ่มใน `INSTALLED_APPS` แล้ว |
| ✅ 1.2 **สร้าง Template พื้นฐาน (`base.html`)**: สร้างไฟล์ `templates/base.html` เป็นโครงหลัก |
| ✅ 1.3 **เพิ่ม Tailwind CSS CDN**: ใน `base.html` |
| ✅ 1.4 สร้าง template `dashboard/home.html` ให้สืบทอดจาก `base.html` |
| ✅ 1.5 สร้าง URL `/dashboard/` และ include `dashboard.urls` ใน `repair_shop/urls.py` |
| ✅ 1.6 สร้าง view `dashboard_home()` เบื้องต้น เพื่อ render `dashboard/home.html` |
| ✅ 1.7 **ทดลองใช้ Tailwind Classes**: ใน `home.html` เพื่อยืนยันการติดตั้ง |

> 📌 **หลังจบเฟสนี้:** มีหน้า Dashboard ว่างๆ ที่ใช้ Tailwind CSS ได้ และมีโครงสร้าง template ที่ถูกต้อง

---

### 📊 **Phase 2: Model `DailySummary` และแสดงข้อมูลสรุปรายวัน/เมื่อวาน**
**(สอดคล้องกับ แผนหลัก ส่วน 2.2, 3.2.1, 4.1 เบื้องต้น)**
**เป้าหมาย:** คำนวณข้อมูล Live ของวันนี้, เก็บข้อมูลสรุปของเมื่อวาน, และแสดงผลทั้งสองส่วน

| รายการ | รายละเอียด |
|--------|-------------|
| ✅ 2.1 **เพิ่ม Model `DailySummary`**: ใน `dashboard/models.py` มีฟิลด์หลัก: `date` (unique), `total_sales_revenue`, `total_repairs_revenue`, `total_revenue`, `total_repairs_profit`, `sales_count`, `repairs_completed_count` (อ้างอิงจาก Model ในแผนหลัก แต่ใช้ชื่อฟิลด์ตามที่ทำไป) |
| ✅ 2.2 รัน `makemigrations dashboard` และ `migrate` |
| ✅ 2.3 **ปรับ Command `generate_daily_summary`**: ให้คำนวณข้อมูลของเมื่อวาน (default) หรือวันที่ระบุ (`--date`) เท่านั้น (เอา `--today` ออก) เพื่อบันทึกลง `DailySummary` |
| ✅ 2.4 **ปรับ View `dashboard_home`**:
    *   คำนวณข้อมูล Live ของ **วันนี้** โดยตรงจาก `Sale` และ `RepairJob`
    *   ดึงข้อมูลสรุปของ **เมื่อวาน** (`yesterday_summary`) จาก `DailySummary` (ถ้ามี)
    *   ส่ง `today_live_data` และ `yesterday_summary` ไปที่ Template |
| ✅ 2.5 **แสดงผลใน Template**:
    *   แสดง Card "ข้อมูล ณ ปัจจุบัน (วันนี้)" โดยใช้ `today_live_data`
    *   แสดง Card "ข้อมูลเมื่อวาน (สรุป)" โดยใช้ `yesterday_summary` (ถ้ามี)
    *   *ปรับปรุงดีไซน์: เพิ่ม Icons, Hover Effects, ปรับสไตล์ Card ให้สวยงามขึ้น* |
| ✅ 2.6 **เพิ่มการจัดการใน Admin**: สร้าง `dashboard/admin.py` และลงทะเบียน `DailySummary` เพื่อให้ดู/แก้ไขข้อมูลผ่านหน้า Admin ได้ |

> 📌 **หลังจบเฟสนี้:** Dashboard แสดงข้อมูล Live ของวันนี้ และข้อมูลสรุปของเมื่อวาน (ถ้ามี) แยกส่วนกันชัดเจน *ดูดีขึ้น* และสามารถจัดการ `DailySummary` ผ่าน Admin ได้

---

### 📈 **Phase 3: กราฟแนวโน้มรายวันและปรับปรุงโมเดล DailySummary**
**(สอดคล้องกับ แผนหลัก ส่วน 4.2, 5 เบื้องต้น และมีการปรับปรุงโมเดล)**
**เป้าหมาย:** เพิ่มกราฟแสดงแนวโน้มข้อมูลย้อนหลัง ปรับปรุงโมเดล DailySummary และสร้างกลไกการอัพเดตข้อมูลอัตโนมัติ

| รายการ | รายละเอียด |
|--------|-------------|
| ✅ 3.1 **ติดตั้ง Chart.js**: เพิ่ม CDN ของ Chart.js ใน `templates/base.html` |
| ✅ 3.2 **เตรียมข้อมูลสำหรับกราฟ**: ปรับ view `dashboard_home` เพื่อดึงข้อมูล `DailySummary` ย้อนหลัง 7 วัน และเตรียมข้อมูลสำหรับกราฟ |
| ✅ 3.3 **สร้าง Canvas Elements และ JavaScript**: ใช้ Chart.js วาดกราฟแนวโน้มข้อมูลต่างๆ |
| ✅ 3.4 **จัดวางและตกแต่งกราฟ**: ใช้ Tailwind CSS ทำให้กราฟสวยงามและตอบสนองต่อขนาดหน้าจอ |
| ☐ 3.5 **เพิ่มฟิลด์พื้นฐานในโมเดล DailySummary**: เพิ่มฟิลด์สำคัญสำหรับการรายงานต่อไปนี้:
    * `total_sales_cost`: ต้นทุนรวมของการขายสินค้า
    * `total_sales_profit`: กำไรรวมจากการขายสินค้า
    * `total_profit`: กำไรรวมทั้งหมด (ขาย+ซ่อม) 
    * `total_labor_charge`: ค่าแรงรวมจากงานซ่อม (สำหรับวิเคราะห์สัดส่วนค่าแรงและชิ้นส่วน) |
| ☐ 3.6 **ปรับปรุง Command `generate_daily_summary`**: ให้คำนวณค่าของฟิลด์ใหม่ทั้งหมด และเพิ่มการคำนวณต้นทุนขายสินค้าจาก `SaleItem` |
| ☐ 3.7 **สร้างฟังก์ชันจัดการข้อมูลใน `dashboard/utils.py`**: สร้างฟังก์ชันสำหรับ:
    * `calculate_daily_sales_metrics(date)`: คำนวณยอดขายและกำไรแบบ real-time
    * `get_best_selling_products(date, limit=5)`: ดึงข้อมูลสินค้าขายดี
    * `calculate_comparison_with_previous(summary, previous_summary)`: เปรียบเทียบกับข้อมูลก่อนหน้า |
| ☐ 3.8 **พัฒนาฟังก์ชันสร้างรายงาน PDF**: เพิ่มฟังก์ชันใน utils:
    * `generate_daily_report_pdf(date)`: สร้างรายงานรายวันเป็น PDF
| ☐ 3.9 **สร้าง View และ URL สำหรับดาวน์โหลดรายงาน**: เพิ่ม:
    * Views: `daily_report_pdf`, `daily_report_excel` 
    * URLs: `/dashboard/reports/daily/pdf/` และ `/dashboard/reports/daily/excel/`
    * ปุ่มดาวน์โหลดรายงานในหน้า dashboard |

> 📌 **หลังจบเฟสนี้:** Dashboard แสดงแนวโน้มรายรับและกำไร, เก็บข้อมูลสำคัญเพิ่มเติมในฐานข้อมูล, มีฟังก์ชันสำหรับวิเคราะห์ข้อมูล, และสามารถดาวน์โหลดรายงานเป็น PDF ได้

---

### 📆 **Phase 4: Model `MonthlySummary` และกราฟรายเดือน**
**(สอดคล้องกับ แผนหลัก ส่วน 2.3, 3.2.2, 4.1)**
**เป้าหมาย:** เพิ่มการสรุปและแสดงผลข้อมูลรายเดือน พร้อมรายงาน PDF/Excel

| รายการ | รายละเอียด |
|--------|-------------|
| ☐ 4.1 **เพิ่ม Model `MonthlySummary`**: ใน `dashboard/models.py` โดยมีฟิลด์:
    * `year`, `month`: ปีและเดือนที่เก็บข้อมูล (unique together)
    * `total_sales_revenue`: รายรับรวมจากการขาย
    * `total_repairs_revenue`: รายรับรวมจากงานซ่อม
    * `total_revenue`: รายรับรวมทั้งหมด
    * `total_sales_cost`: ต้นทุนรวมของการขาย
    * `total_repairs_cost`: ต้นทุนรวมของงานซ่อม
    * `total_profit`: กำไรรวมทั้งหมด
    * `total_labor_charge`: ค่าแรงรวมจากงานซ่อม
    * `sales_count`: จำนวนรายการขาย
    * `repairs_completed_count`: จำนวนงานซ่อมที่เสร็จ |
| ☐ 4.2 รัน `makemigrations` และ `migrate` |
| ☐ 4.3 **สร้าง Command `generate_monthly_summary`**: คำนวณข้อมูลสรุปรายเดือน โดยรวมจาก `DailySummary` ของเดือนนั้นๆ |
| ☐ 4.4 **ปรับ View**: ให้ดึงข้อมูล `MonthlySummary` ล่าสุด (เช่น 6 เดือนย้อนหลัง) |
| ☐ 4.5 **แสดงผลรายเดือน**: เพิ่มส่วนแสดงข้อมูลสรุปของเดือนล่าสุดในรูปแบบ Card |
| ☐ 4.6 **สร้างกราฟรายเดือน**: เพิ่ม Bar Chart แสดงยอดขายรวมและกำไรเปรียบเทียบแต่ละเดือนย้อนหลัง |
| ☐ 4.7 **เพิ่มฟังก์ชันสร้างรายงานเดือน**:
    * `generate_monthly_report_pdf(year, month)`: สร้างรายงานรายเดือนเป็น PDF
    * `generate_monthly_report_excel(year, month)`: สร้างรายงานรายเดือนเป็น Excel |
| ☐ 4.8 **เพิ่ม Views และ URLs สำหรับรายงานเดือน**:
    * URLs: `/dashboard/reports/monthly/pdf/` และ `/dashboard/reports/monthly/excel/` |

> 📌 **หลังจบเฟสนี้:** Dashboard แสดงข้อมูลสรุปและกราฟเปรียบเทียบรายเดือน พร้อมความสามารถดาวน์โหลดรายงานรายเดือน

---

### 📦 **Phase 5: Model `ProductStatistics` และแสดงข้อมูลสินค้า**
**(สอดคล้องกับ แผนหลัก ส่วน 2.4, 3.1 (อาจจะต้องเพิ่ม signal), 4.1)**
**เป้าหมาย:** วิเคราะห์และแสดงข้อมูลเกี่ยวกับสินค้า

| รายการ | รายละเอียด |
|--------|-------------|
| ☐ 5.1 **เพิ่ม Model `ProductStatistics`**: ใน `dashboard/models.py` มีฟิลด์: `product` (OneToOne), `total_sales_quantity`, `total_repair_usage`, `total_sales_revenue`, `last_updated` (ฟิลด์อื่น ๆ ตามแผนหลักอาจเพิ่มทีหลัง) |
| ☐ 5.2 รัน `makemigrations` และ `migrate` |
| ☐ 5.3 **สร้างกลไกอัปเดต**:
    *   (ทางเลือก 1) สร้าง Command `update_product_stats` เพื่อคำนวณข้อมูลใหม่ทั้งหมด
    *   (ทางเลือก 2) สร้าง Signals เมื่อมีการสร้าง `SaleItem` หรือ `UsedPart` เพื่ออัปเดต `ProductStatistics` ที่เกี่ยวข้อง (อาจซับซ้อนกว่า) |
| ☐ 5.4 **ปรับ View**: ให้ดึงข้อมูลสินค้าขายดี Top 5 (เรียงตาม `total_sales_revenue` หรือ `total_sales_quantity`) |
| ☐ 5.5 **แสดงผลสินค้า**: เพิ่มส่วนแสดงผล (เช่น ตาราง หรือ List group) แสดงรายการสินค้าขายดี Top 5 ใน `home.html` |
| ☐ 5.6 **(Optional) กราฟสินค้า**: เพิ่ม Doughnut/Pie Chart แสดงสัดส่วนยอดขายของสินค้า Top 5 |

> 📌 **หลังจบเฟสนี้:** Dashboard แสดงข้อมูลสินค้าขายดี Top 5 ได้

---

### 👤 **Phase 6: Model `CustomerInsights` และแสดงข้อมูลลูกค้า**
**(สอดคล้องกับ แผนหลัก ส่วน 2.5, 3.1, 4.1)**
**เป้าหมาย:** วิเคราะห์และแสดงข้อมูลเกี่ยวกับลูกค้า

| รายการ | รายละเอียด |
|--------|-------------|
| ☐ 6.1 **เพิ่ม Model `CustomerInsights`**: ใน `dashboard/models.py` มีฟิลด์: `customer` (OneToOne), `total_spent`, `total_repair_jobs`, `total_sales`, `latest_visit_date` |
| ☐ 6.2 รัน `makemigrations` และ `migrate` |
| ☐ 6.3 **สร้างกลไกอัปเดต**: คล้ายกับ `ProductStatistics` (ใช้ Command หรือ Signals จาก `Sale` และ `RepairJob`) |
| ☐ 6.4 **ปรับ View**: ให้ดึงข้อมูลลูกค้าที่มียอดใช้จ่ายสูงสุด Top 5 (เรียงตาม `total_spent`) |
| ☐ 6.5 **แสดงผลลูกค้า**: เพิ่มส่วนแสดงผลลูกค้า Top 5 ใน `home.html` |

> 📌 **หลังจบเฟสนี้:** Dashboard แสดงข้อมูลลูกค้า Top 5 ที่มียอดใช้จ่ายสูงสุดได้

---

### 🔔 **Phase 7: ระบบแจ้งเตือนและการแสดงสถานะ**
**(สอดคล้องกับ แผนหลัก ส่วน 2.6, 3.1.3, 4.1)**
**เป้าหมาย:** สร้างระบบแจ้งเตือนหลายรูปแบบสำหรับร้านซ่อมขนาดเล็ก

| รายการ | รายละเอียด |
|--------|-------------|
| ☐ 7.1 **เพิ่ม Model `InventoryAlert`**: ใน `dashboard/models.py` มีฟิลด์: `product`, `alert_type` (LOW_STOCK, OUT_OF_STOCK), `message`, `created_at`, `resolved` |
| ☐ 7.2 **เพิ่ม Model `RepairAlert`**: เพื่อแจ้งเตือนงานซ่อมค้างนาน มีฟิลด์: `repair_job`, `alert_type` (OVERDUE, PENDING_PAYMENT), `message`, `days_pending`, `created_at`, `resolved` |
| ☐ 7.3 **รัน `makemigrations` และ `migrate`** |
| ☐ 7.4 **สร้าง Signal**: 
    * สร้าง Signal `post_save` บน Model `Stock` เพื่อตรวจสอบสินค้าใกล้หมด/หมดสต็อก
    * สร้าง Signal `post_save` บน Model `RepairJob` เพื่อตรวจสอบงานซ่อมค้างนาน |
| ☐ 7.5 **ปรับ View `dashboard_home`**: 
    * ดึงการแจ้งเตือนทั้งหมดที่ยังไม่ resolved
    * ดึงงานซ่อมค้างนานเกิน 7 วัน
    * ดึงรายการที่ยังไม่ชำระเงิน |
| ☐ 7.6 **สร้าง section แจ้งเตือนในหน้า home**: แสดงรายการแจ้งเตือนแยกตามหมวดหมู่พร้อมไอคอนและสีที่ชัดเจน |
| ☐ 7.7 **สร้าง View สำหรับจัดการแจ้งเตือน**: 
    * `inventory_alerts`: หน้ารายละเอียดการแจ้งเตือนสินค้าคงคลัง
    * `repair_alerts`: หน้ารายละเอียดการแจ้งเตือนงานซ่อม
    * สามารถ mark resolved ได้จากหน้านี้ |
| ☐ 7.8 **สร้างรายงานการแจ้งเตือน PDF**: สามารถพิมพ์รายงานสินค้าใกล้หมด/งานค้างได้ |

> 📌 **หลังจบเฟสนี้:** Dashboard มีระบบแจ้งเตือนที่ครอบคลุมทั้งสินค้าคงคลัง งานซ่อมค้าง และการชำระเงิน พร้อมความสามารถในการจัดการแจ้งเตือนและพิมพ์รายงาน

---

### 🧪 **Phase 8: เพิ่มการทดสอบ**
**(สอดคล้องกับ แผนหลัก ส่วน 6)**
**เป้าหมาย:** ทำให้ระบบน่าเชื่อถือและป้องกันข้อผิดพลาด

| รายการ | รายละเอียด |
|--------|-------------|
| ☐ 8.1 **เขียน Unit Tests**: ทดสอบ Model, Command และ Functions/Utils ที่เกี่ยวข้องกับการคำนวณข้อมูลสรุป |
| ☐ 8.2 **เขียน Integration Tests**: ทดสอบการทำงานร่วมกันของ Signals, Commands และ Views (เช่น ทดสอบว่าเมื่อ Stock เหลือน้อย Alert ถูกสร้าง และแสดงผลใน View ถูกต้อง) |

> 📌 **หลังจบเฟสนี้:** มี Test Coverage ที่ดีขึ้น มั่นใจในความถูกต้องของข้อมูลและการทำงาน

---

## 🔚 สรุป (ฉบับละเอียด)

| เฟส | สิ่งที่ได้ | โมเดลหลักที่เกี่ยวข้อง |
|-----|-------------|----------------------|
| 1   | หน้า Dashboard พื้นฐาน + Tailwind | - |
| 2   | แสดงข้อมูลสรุปรายวัน/เมื่อวาน | `DailySummary` |
| 3   | กราฟแนวโน้ม + ปรับปรุงโมเดล + รายงาน PDF | `DailySummary` + ระบบรายงาน |
| 4   | ข้อมูลรายเดือน + กราฟ + รายงานเดือน | `MonthlySummary` + ระบบรายงาน |
| 5   | แสดงข้อมูลสินค้าขายดี Top 5 | `ProductStatistics` |
| 6   | แสดงข้อมูลลูกค้า Top 5 | `CustomerInsights` |
| 7   | ระบบแจ้งเตือนสินค้า/งานซ่อม/การชำระเงิน | `InventoryAlert`, `RepairAlert` |
| 8   | เพิ่มการทดสอบ (Unit/Integration) | ทุกโมเดล |

---
