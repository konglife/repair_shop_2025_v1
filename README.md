# Repair Shop Management System v1

## Project Overview

This project is a modern web application designed to streamline the operations of a repair shop. It aims to provide a comprehensive solution for managing customer information, repair orders, inventory, and potentially other aspects of a repair business.

## Features

*   **Customer Management:** (e.g., Add, view, edit customer details)
*   **Repair Order Management:** (e.g., Create, track, update repair statuses)
*   **Inventory Management:** (e.g., Manage parts, track stock levels)
*   **Reporting & Analytics:** (e.g., Generate reports on sales, repairs)
*   **User Authentication & Authorization:** (e.g., Secure login for staff)
*   **(Add more specific features here based on your application's functionality)**

## Technologies Used

*   **Backend:** Python, Django
*   **Database:** (e.g., PostgreSQL, SQLite, MySQL)
*   **Frontend:** (e.g., HTML, CSS, JavaScript, [Any specific framework like React, Vue, Angular if used])
*   **Other Libraries/Tools:** (e.g., Django REST Framework, Celery, Redis, etc.)

## Installation

Follow these steps to set up the project locally for development:

### 1. Clone the repository

```bash

## การรันคำสั่งสรุปรายวันและรายเดือน (DEV)

สำหรับนักพัฒนา/ทดสอบ สามารถสร้างหรืออัปเดตข้อมูลสรุปรายวันและรายเดือนเพื่อให้ Dashboard แสดงข้อมูลที่ถูกต้องได้ดังนี้:

### สรุปรายวัน (Daily Summary)

สร้างหรืออัปเดตข้อมูลสรุปรายวัน:
```bash
python manage.py generate_daily_summary --date=YYYY-MM-DD --force
```
- `--date=YYYY-MM-DD` : ระบุวันที่ที่ต้องการสร้าง/อัปเดต (ตัวอย่าง: `--date=2025-06-06`)
- `--force` : (ไม่บังคับ) ใช้ถ้าต้องการบังคับให้สร้างใหม่แม้จะมีข้อมูลเดิม
- ถ้าไม่ระบุ `--date` จะสร้างของเมื่อวานให้อัตโนมัติ

ตัวอย่าง:
```bash
python manage.py generate_daily_summary --date=2025-06-06 --force
```

### สรุปรายเดือน (Monthly Summary)

สร้างหรืออัปเดตข้อมูลสรุปรายเดือน:
```bash
python manage.py generate_monthly_summary --month=YYYY-MM --force
```
- `--month=YYYY-MM` : ระบุเดือนที่ต้องการสร้าง/อัปเดต (ตัวอย่าง: `--month=2025-05`)
- `--months-back=N` : (ไม่บังคับ) สร้างย้อนหลัง N เดือน (default=1)
- `--force` : (ไม่บังคับ) ใช้ถ้าต้องการบังคับให้สร้างใหม่แม้จะมีข้อมูลเดิม
- ถ้าไม่ระบุ `--month` จะสร้างของเดือนก่อนหน้าให้อัตโนมัติ

ตัวอย่าง:
```bash
python manage.py generate_monthly_summary --month=2025-05 --force
```

git clone https://github.com/konglife/repair_shop_2025_v1.git
cd repair_shop_2025_v1
```

### 2. Create and activate a virtual environment

```bash
# For Windows
python -m venv env
.\env\Scripts\activate

# For macOS/Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate inventory
```

### 5. Create a Superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The application should now be accessible at `http://127.0.0.1:8000/`.

## Project Structure

```
repair_shop_2025_v1/
├── repair_shop/          # Main Django project settings
├── dashboard/            # Core application for dashboard features
├── customers/            # Application for customer management
├── inventory/            # Application for inventory management
├── sales/                # Application for sales and repair order management
├── env/                  # Python virtual environment
├── static/               # Static files (CSS, JS, images)
├── media/                # User-uploaded media files
├── templates/            # Global HTML templates
├── requirements.txt      # Python dependencies
├── manage.py             # Django's command-line utility
└── README.md             # Project documentation
```

## Application Logic (High-Level)

*(This section should describe the main workflows and how different parts of the application interact. You'll need to fill this in with details specific to your implementation.)*

*   **Customer Flow:** (e.g., How new customers are added, how their repair history is tracked.)
*   **Repair Process:** (e.g., Steps from creating a repair order to completing it, status updates.)
*   **Inventory Integration:** (e.g., How parts are deducted from inventory when used in a repair.)
*   **Reporting:** (e.g., How data is aggregated for daily/monthly reports.)

## Contributing

We welcome contributions to this project! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add new feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details. (If you have a different license, update this accordingly or create a LICENSE file.)

---

**Note:** This README provides a general structure. Please fill in the bracketed placeholders `[]` and expand on the sections with details specific to your `repair_shop_2025_v1` project.

1. **การเพิ่มการเปลี่ยนแปลงในอนาคต**:
   - เมื่อคุณมีการเปลี่ยนแปลงเพิ่มเติมในโปรเจคของคุณ:
     ```bash
     git add .
     git commit -m "ลูกค้าเสร็จแล้ว"
     git push
     ```
   - คุณสามารถทำการ push ได้เลยเพราะครั้งแรกคุณได้กำหนด `-u origin main` แล้ว.

   2. **อัปเดตหรือดึงข้อมูลจาก GitHub**:
     - เพื่อดึงการเปลี่ยนแปลงเหล่านั้นมาอัปเดตโปรเจคในเครื่องของคุณ:
     ```bash
     git pull origin main
     ```

     ---
