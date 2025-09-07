import os
import pika
import json
import time
import sys
from bson import json_util

from router_client import get_interfaces
from database import save_interface_status


def callback(ch, method, properties, body):
    job = json.loads(body.decode(), object_hook=json_util.object_hook)
    ip = job.get("ip")
    username = job.get("username")
    password = job.get("password")

    print(f"[*] Received job for router: {ip}")

    try:
        print(f"  - Connecting to {ip} to get interfaces...")
        interface_data = get_interfaces(ip, username, password)

        if interface_data:
            print(json.dumps(interface_data, indent=2))
            save_interface_status(ip, interface_data)
            print(f"  - Successfully stored interface status for {ip}")
        else:
            print(f"  - No interface data received from {ip}")

    except Exception as e:
        print(f"  - [ERROR] Failed to process job for {ip}: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("-" * 20)


def main():
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    connection = None

    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=rabbitmq_host)
            )
            print(f"Worker connected to RabbitMQ at {rabbitmq_host} successfully!")
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Worker: RabbitMQ not ready, retrying... (Attempt {i+1})")
            time.sleep(5)

    if not connection:
        print("Worker: Could not connect to RabbitMQ. Exiting.")
        sys.exit(1)

    channel = connection.channel()
    channel.queue_declare(queue="router_jobs")
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="router_jobs", on_message_callback=callback)

    print("[*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
