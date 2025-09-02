import os
from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
routers_collection = db["routers"]
interface_status_collection = db["interface_status"]

@app.route("/", methods=["GET"])
def index():
    all_routers = list(routers_collection.find())
    return render_template("index.html", routers=all_routers)

@app.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")
    if ip and username and password:
        routers_collection.insert_one({"ip": ip, "username": username, "password": password})
    return redirect(url_for('index'))

@app.route("/delete/<id>", methods=["POST"])
def delete_router(id):
    routers_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

@app.route("/router/<ip>", methods=["GET"])
def router_detail(ip):
    status_list = list(interface_status_collection.find({"router_ip": ip}).sort("timestamp", -1).limit(3))
    return render_template("router_detail.html", ip=ip, status_list=status_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
