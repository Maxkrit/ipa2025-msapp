import os
from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# เชื่อม MongoDB ผ่าน hostname ของ container mongo
mongo_uri = os.getenv("MONGO_URI", "mongodb://mongo:27017")
client = MongoClient(mongo_uri)
db = client["routerdb"]
collection = db["comments"]

@app.route("/")
def main():
    data = list(collection.find())
    return render_template("index.html", data=data)

@app.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    yourname = request.form.get("yourname")
    message = request.form.get("message")
    if ip and yourname and message:
        collection.insert_one({"ip": ip, "yourname": yourname, "message": message})
    return redirect("/")

@app.route("/delete/<id>", methods=["POST"])
def delete_comment(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
