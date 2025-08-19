#!/bin/bash

# เตรียมโฟลเดอร์สำหรับ build context
rm -rf tempdir
mkdir -p tempdir/templates
mkdir -p tempdir/static

# คัดลอกไฟล์ที่จำเป็นทั้งหมดเข้าไปใน tempdir
cp app.py tempdir/.
cp requirements.txt tempdir/.
cp -r templates/* tempdir/templates/.
cp -r static/* tempdir/static/.


# --- สร้าง Dockerfile ทีละบรรทัดด้วยคำสั่ง echo ตามสไตล์เดิม ---
echo "FROM python:3.12-slim" > tempdir/Dockerfile
echo "WORKDIR /app" >> tempdir/Dockerfile

echo "COPY requirements.txt ." >> tempdir/Dockerfile
echo "RUN pip3 install --no-cache-dir --progress-bar off -r requirements.txt" >> tempdir/Dockerfile

echo "COPY ./static ./static/" >> tempdir/Dockerfile
echo "COPY ./templates ./templates/" >> tempdir/Dockerfile
echo "COPY app.py ." >> tempdir/Dockerfile

echo "EXPOSE 8080" >> tempdir/Dockerfile
echo "CMD [\"python3\", \"app.py\"]" >> tempdir/Dockerfile


# --- ส่วนของคำสั่ง Docker ที่แก้ไขให้ทำงานได้อย่างถูกต้อง ---
cd tempdir

# สร้าง network ถ้ายังไม่มี
if [ -z "$(docker network ls --filter name=^app-net$ --format="{{ .Name }}")" ]; then
    docker network create app-net
fi

# หยุดและลบ container เก่าทิ้งก่อน เพื่อป้องกันชื่อซ้ำ
docker stop web mongo || true
docker rm web mongo || true

# Build Docker image
docker build -t my-web-app .

# รัน MongoDB container
docker run -d \
    -p 27017:27017 \
    --network app-net \
    -v mongo-data:/data/db \
    --name mongo mongo:6

# รัน Web App container
docker run -d \
    -p 8080:8080 \
    --network app-net \
    --name web web

# แสดง container ทั้งหมดที่กำลังทำงาน
docker ps -a 
