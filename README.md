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

```bash
source ../env/Scripts/activate
```


```bash
python manage.py runserver
```
python manage.py makemigrations
