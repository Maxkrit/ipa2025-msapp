import os
import pika
import json
import time
import sys
from datetime import datetime
from pymongo import MongoClient
from bson import json_util

print("Worker is starting...")

# ส่วนเชื่อมต่อ Mongo ไม่ต้องแก้ เพราะอ่าน MONGO_URI จาก .env อยู่แล้ว
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("DB_NAME")
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
interface_status_collection = db["interface_status"]

def process_job(body):
    router_data = json.loads(body, object_hook=json_util.object_hook)
    ip = router_data.get("ip")
    print(f"  - Received job for router: {ip}")
    mock_interface_data = [
        {"interface": "GigabitEthernet0/0", "ip_address": ip, "status": "up", "proto": "up"},
        {"interface": "GigabitEthernet0/1", "ip_address": "unassigned", "status": "down", "proto": "down"}
    ]
    interface_status_collection.insert_one({
        "router_ip": ip,
        "interfaces": mock_interface_data,
        "timestamp": datetime.utcnow()
    })
    print(f"  - Stored interface status for {ip}")

def main():
    # อ่านค่า IP จาก .env, ถ้าไม่มีให้ใช้ชื่อ 'rabbitmq' เป็นค่าสำรอง
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    connection = None

    # พยายามเชื่อมต่อซ้ำๆ
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            print(f"Worker connected to RabbitMQ at {rabbitmq_host} successfully!")
            break # ถ้าสำเร็จ ให้ออกจาก loop
        except pika.exceptions.AMQPConnectionError:
            print(f"Worker: RabbitMQ at {rabbitmq_host} not ready, retrying in 5 seconds... (Attempt {i+1}/10)")
            time.sleep(5)
    
    if not connection:
        print(f"Worker: Could not connect to RabbitMQ at {rabbitmq_host} after multiple attempts. Exiting.")
        sys.exit(1)

    # ส่วนที่เหลือทำงานเหมือนเดิม
    channel = connection.channel()
    channel.queue_declare(queue='router_jobs')

    def callback(ch, method, properties, body):
        process_job(body.decode())
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='router_jobs', on_message_callback=callback)

    print('[*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
