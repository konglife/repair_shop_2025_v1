# แผนการพัฒนา Dashboard (API-First Approach)

เอกสารนี้สรุปแผนการพัฒนา Dashboard ใหม่โดยใช้สถาปัตยกรรมแบบ API-First ซึ่งแยกส่วน Backend และ Frontend ออกจากกันอย่างชัดเจน เพื่อความยืดหยุ่น, ปลอดภัย, และง่ายต่อการบำรุงรักษาในระยะยาว

- **Backend:** Django, Django REST Framework (DRF)
- **Frontend:** SvelteKit
- **Authentication:** Token-Based (JWT)

---

## Phase 1: การเตรียมโปรเจกต์และล้างของเก่า (Project Prep & Cleanup)

**เป้าหมาย:** เตรียมพื้นที่ทำงานให้พร้อมสำหรับการพัฒนา API โดยลบส่วนประกอบของ Dashboard เดิม (ที่ใช้ DTL) ออกไปก่อน

1.  **สร้าง Branch ใหม่ (สำคัญที่สุด):** เพื่อแยกการพัฒนาออกจาก `main` branch
    ```bash
    git checkout -b feature/dashboard-api
    ```

2.  **ลบส่วนหน้าบ้านเดิม (DTL Components):** ใน Branch ใหม่นี้ ให้ทำการลบ:
    - **ไฟล์ Template:** `dashboard/templates/dashboard/home.html`
    - **ฟังก์ชัน View:** ลบ `dashboard_home` ใน `dashboard/views.py`
    - **การตั้งค่า URL:** ลบ `path` ที่ชี้ไปยัง `dashboard_home` ใน `dashboard/urls.py`

3.  **บันทึกการเปลี่ยนแปลง (Commit):**
    ```bash
    git add .
    git commit -m "Refactor: Remove DTL components for API-first approach"
    ```

---

## Phase 2: การสร้าง Backend API ด้วย Django REST Framework (DRF)

**เป้าหมาย:** สร้าง API ที่ปลอดภัยและมีประสิทธิภาพเพื่อส่งข้อมูลให้ Frontend

1.  **ติดตั้ง Packages ที่จำเป็น:**
    ```bash
    pip install djangorestframework djangorestframework-simplejwt
    # เพิ่ม package ใน requirements.txt
    ```

2.  **ตั้งค่าใน `settings.py`:**
    - เพิ่ม `'rest_framework'` และ `'rest_framework_simplejwt'` ใน `INSTALLED_APPS`
    - กำหนดค่า `REST_FRAMEWORK` ให้ใช้ `JWTAuthentication` เป็น default

3.  **สร้าง API Endpoints:** (ทุก Endpoint ต้องมีการยืนยันตัวตน)
    - **Authentication:**
        - `POST /api/token/`: สำหรับ Login เพื่อรับ Access/Refresh tokens
        - `POST /api/token/refresh/`: สำหรับขอ Access token ใหม่
    - **Data Endpoints:**
        - `GET /api/dashboard/summary/today/`: ข้อมูลสรุปรายวัน (Live)
        - `GET /api/dashboard/summary/monthly/`: ข้อมูลสรุปเดือนปัจจุบัน (Live)
        - `GET /api/dashboard/charts/daily/?start_date=...&end_date=...`: ข้อมูลสำหรับกราฟรายวัน (จาก `DailySummary`)
        - `GET /api/dashboard/charts/monthly/`: ข้อมูลสำหรับกราฟรายเดือน (จาก `DailySummary`)
        - `GET /api/dashboard/products/best-selling/`: ข้อมูลสินค้าขายดี

4.  **Business Logic:**
    - นำฟังก์ชันการคำนวณต่างๆ ที่มีอยู่แล้วใน `dashboard/utils.py` มาใช้เป็น Logic หลักในการประมวลผลข้อมูลสำหรับแต่ละ Endpoint

---

## Phase 3: การสร้าง Frontend Dashboard ด้วย SvelteKit

**เป้าหมาย:** สร้างหน้า Dashboard ที่สวยงาม ทันสมัย และใช้งานง่าย โดยดึงข้อมูลจาก API ที่สร้างไว้

1.  **ตั้งค่าโปรเจกต์ SvelteKit:** สร้างโปรเจกต์ใหม่ในโฟลเดอร์แยก

2.  **สร้างหน้า Login:**
    - สร้างฟอร์ม Login เพื่อรับ `username` และ `password`
    - ส่งข้อมูลไปที่ `POST /api/token/` เพื่อรับ JWT และจัดเก็บใน Browser อย่างปลอดภัย (เช่นใน `localStorage` หรือ `cookie`)

3.  **สร้างหน้า Dashboard:**
    - ออกแบบ Layout และ UI Components (การ์ด, กราฟ, ตาราง)
    - เขียนโค้ดเพื่อเรียกใช้ API ใน Phase 2 โดยต้องแนบ `Access Token` ไปใน `Authorization` header ของทุก Request
    - นำข้อมูลที่ได้รับมาแสดงผล (อาจใช้ Library เช่น `Chart.js` หรือ `ECharts` เพื่อสร้างกราฟ)

---

## Phase 4: การรวมโค้ดและเตรียม Deploy (Integration & Deployment)

**เป้าหมาย:** นำโค้ดที่พัฒนาเสร็จแล้วมารวมกันและนำขึ้นใช้งานจริง

1.  **สร้าง Pull Request (PR):** เมื่อพัฒนาใน `feature/dashboard-api` เสร็จสิ้น ให้สร้าง PR บน GitHub เพื่อขอนำโค้ดกลับไปรวมที่ `main`

2.  **Code Review และ Merge:** ตรวจสอบความเรียบร้อยของโค้ดใน PR และทำการ Merge

3.  **Deployment:**
    - **Backend (Django):** Deploy โปรเจกต์ Django ขึ้น Server ตามปกติ
    - **Frontend (SvelteKit):** Build โปรเจกต์ให้เป็น Static files (`npm run build`) แล้วนำไป deploy บนบริการ Hosting สำหรับ Frontend เช่น Vercel หรือ Netlify (แนะนำ)
