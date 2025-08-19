#!/bin/bash

# --- 1. ทำความสะอาดสภาพแวดล้อม (Cleanup Step) ---
echo "--- 1. Cleaning up ALL previous Docker environments ---"

# หยุดและลบ container ที่สร้างจาก Docker Compose (ถ้ามี)
# The '--project-directory .' ensures it looks for containers related to the current folder's compose file.
docker compose --project-directory . down --remove-orphans >/dev/null 2>&1 || true

# หยุดและลบ container ที่สร้างจาก script นี้ (ถ้ามี)
docker stop web mongo >/dev/null 2>&1 || true
docker rm web mongo >/dev/null 2>&1 || true

# ลบ network เก่า (ถ้ามี)
docker network rm app-net >/dev/null 2>&1 || true

echo "Cleanup complete."


# --- 2. เตรียมโฟลเดอร์สำหรับ Build ---
echo "--- 2. Preparing build directory ---"
rm -rf tempdir
mkdir -p tempdir/templates
mkdir -p tempdir/static

# คัดลอกไฟล์ที่จำเป็นทั้งหมด
cp app.py tempdir/.
cp requirements.txt tempdir/.
cp -r templates/* tempdir/templates/.
cp -r static/* tempdir/static/.


# --- 3. สร้าง Dockerfile ---
echo "--- 3. Generating Dockerfile ---"
cat > tempdir/Dockerfile << EOF
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
EOF
echo "Dockerfile created."


# --- 4. เริ่ม Build และ Run ---
cd tempdir

echo "--- 4. Building 'web' image ---"
docker build -t web .

echo "--- 5. Creating network 'app-net' ---"
docker network create app-net

echo "--- 6. Starting 'mongo' container ---"
docker run -d \
    --name mongo \
    --network app-net \
    -p 27017:27017 \
    -v mongo-data:/data/db \
    mongo:6

echo "--- 7. Starting 'web' container ---"
docker run -d \
    --name web \
    --network app-net \
    -p 8080:8080 \
    web

cd ..


# --- 8. แสดงผลลัพธ์ ---
echo ""
echo "--- 8. Setup complete! Showing ONLY running containers managed by this script: ---"
# ใช้ filter เพื่อแสดงเฉพาะ container ที่เราสนใจจริงๆ
docker ps --filter "name=web" --filter "name=mongo"
