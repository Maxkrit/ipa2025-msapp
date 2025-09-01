import time
import json
import pika
from bson import json_util
from database import get_router_info

INTERVAL = 10.0 # ทำงานทุก 10 วินาที

def produce(body):
    connection = None
    for i in range(10): # พยายามเชื่อมต่อ 10 ครั้ง
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            break # ถ้าสำเร็จ ให้ออกจาก loop
        except pika.exceptions.AMQPConnectionError:
            print(f"Scheduler: RabbitMQ not ready, retrying in 5 seconds... (Attempt {i+1}/10)")
            time.sleep(5)
    
    if not connection:
        print("Scheduler: Could not connect to RabbitMQ after multiple attempts. Skipping this cycle.")
        return

    channel = connection.channel()
    channel.queue_declare(queue="router_jobs")
    channel.basic_publish(
        exchange="",
        routing_key="router_jobs",
        body=body
    )
    connection.close()

def scheduler():
    print("Scheduler is starting...")
    while True:
        start_time = time.time()
        print(f"[{time.ctime(start_time)}] Scheduler running job...")

        try:
            router_list = get_router_info()
            if not router_list:
                print("  - No routers found in database.")
            else:
                print(f"  - Found {len(router_list)} routers. Sending to RabbitMQ...")
                for router in router_list:
                    message_body = json.dumps(router, default=json_util.default)
                    produce(message_body)
                    print(f"    - Sent job for router: {router.get('ip', 'N/A')}")
        
        except Exception as e:
            print(f"An error occurred in scheduler loop: {e}")

        time_to_wait = INTERVAL - (time.time() - start_time)
        if time_to_wait > 0:
            time.sleep(time_to_wait)

if __name__ == '__main__':
    # ไม่ต้อง sleep ที่นี่แล้ว เพราะ logic การ retry อยู่ในฟังก์ชัน produce
    scheduler()
