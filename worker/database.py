import os
from pymongo import MongoClient
from datetime import datetime


def save_interface_status(router_ip, interfaces):
    """
    บันทึกผลลัพธ์ Interface status ลงใน MongoDB.
    """
    MONGO_URI = os.environ.get("MONGO_URI")
    DB_NAME = os.environ.get("DB_NAME")

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["interface_status"]  # เก็บใน collection ใหม่

    data = {
        "router_ip": router_ip,
        "interfaces": interfaces,
        "timestamp": datetime.utcnow(),
    }

    collection.insert_one(data)
    client.close()
