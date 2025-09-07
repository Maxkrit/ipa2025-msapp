import os
import pika
import time


def produce(body):
    rabbitmq_host = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    connection = None

    for i in range(10):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(rabbitmq_host)
            )
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"Scheduler: RabbitMQ not ready, retrying... (Attempt {i+1})")
            time.sleep(5)

    if not connection:
        print("Scheduler: Could not connect to RabbitMQ. Aborting.")
        return

    channel = connection.channel()
    channel.queue_declare(queue="router_jobs")
    channel.basic_publish(exchange="", routing_key="router_jobs", body=body)
    connection.close()
