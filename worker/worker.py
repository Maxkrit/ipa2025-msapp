import os
import pika
import json
import time
import sys
from datetime import datetime
from pymongo import MongoClient
from bson import json_util

# Import ฟังก์ชันที่เราสร้างขึ้นจากไฟล์อื่น
from router_client import get_interfaces
from database import save_interface_status

def callback(ch, method, properties, body):
    """
    ฟังก์ชันนี้จะถูกเรียกใช้งานทุกครั้งที่มี message ใหม่เข้ามา
    """
    # 1. แปลง message จาก JSON string กลับเป็น Python dictionary
    job = json.loads(body.decode(), object_hook=json_util.object_hook)
    ip = job.get("ip")
    username = job.get("username")
    password = job.get("password")
    
    print(f"[*] Received job for router: {ip}")

    try:
        # 2. เรียกใช้ router_client เพื่อดึงข้อมูลจาก Router
        print(f"  - Connecting to {ip} to get interfaces...")
        interface_data = get_interfaces(ip, username, password)
        
        if interface_data:
            # --- [ เพิ่มตรงนี้ ] ---
            # แสดงผลลัพธ์ JSON ที่ได้จาก Router ใน Log
            print(json.dumps(interface_data, indent=2))
            # --------------------

            # 3. เรียกใช้ database client เพื่อบันทึกผลลัพธ์
            save_interface_status(ip, interface_data)
            print(f"  - Successfully stored interface status for {ip}")
        else:
            print(f"  - No interface data received from {ip}")

    except Exception as e:
        print(f"  - [ERROR] Failed to process job for {ip}: {e}")
    
    # 4. ส่ง tín hiệu "ack" กลับไปบอก RabbitMQ ว่าทำงานเสร็จแล้ว
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("-" * 20)


def main():
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    connection = None

    # พยายามเชื่อมต่อ RabbitMQ ซ้ำๆ
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            print(f"Worker connected to RabbitMQ at {rabbitmq_host} successfully!")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Worker: RabbitMQ at {rabbitmq_host} not ready, retrying... (Attempt {i+1})")
            time.sleep(5)
    
    if not connection:
        print("Worker could not connect to RabbitMQ. Exiting.")
        sys.exit(1)

    channel = connection.channel()
    channel.queue_declare(queue='router_jobs')
    
    # บอก RabbitMQ ให้ส่งงานมาให้ worker ทีละ 1 งานเท่านั้น
    channel.basic_qos(prefetch_count=1)
    
    # เริ่มรอรับ message จาก queue และผูกกับฟังก์ชัน callback
    channel.basic_consume(queue='router_jobs', on_message_callback=callback)

    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        # Properly exit on Ctrl+C
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)