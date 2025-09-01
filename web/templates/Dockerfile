# ใช้ Python 3.12-slim เป็น base image
FROM python:3.12-slim

# ตั้งค่า working directory ภายใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt เข้าไปใน container
COPY requirements.txt .

# ติดตั้ง library ที่ต้องการ
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกไฟล์ทั้งหมดในโฟลเดอร์ web เข้าไปใน container
COPY . .

# คำสั่งที่จะรันเมื่อ container เริ่มทำงาน
CMD ["python", "app.py"]
