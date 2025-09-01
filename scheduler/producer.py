import os
import pika
import time

def produce(body):
    # อ่านค่า IP จาก .env, ถ้าไม่มีให้ใช้ชื่อ 'rabbitmq' เป็นค่าสำรอง
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    connection = None

    # พยายามเชื่อมต่อซ้ำๆ
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
            break # ถ้าสำเร็จ ให้ออกจาก loop
        except pika.exceptions.AMQPConnectionError:
            print(f"Scheduler: RabbitMQ at {rabbitmq_host} not ready, retrying in 5 seconds... (Attempt {i+1}/10)")
            time.sleep(5)
    
    if not connection:
        print(f"Scheduler: Could not connect to RabbitMQ at {rabbitmq_host}. Skipping this cycle.")
        return

    # ส่วนที่เหลือทำงานเหมือนเดิม
    channel = connection.channel()
    channel.queue_declare(queue="router_jobs")
    channel.basic_publish(
        exchange="",
        routing_key="router_jobs",
        body=body
    )
    connection.close()
