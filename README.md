# สร้าง virtual environment
python -m venv venv

# เปิดใช้งาน (Windows)
venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน migrations
python manage.py migrate

# สร้าง superuser
python create_superuser.py


# คัดลอก env_example.txt เป็น .env
cp env_example.txt .env

# แก้ไข .env ตามต้องการ
# SECRET_KEY=your-secret-key-here
# DEBUG=True
# ALLOWED_HOSTS=localhost,127.0.0.1

# รัน Django server
python manage.py runserver

# เปิดเบราว์เซอร์ไปที่
# http://127.0.0.1:8000/
