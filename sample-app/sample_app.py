from flask import Flask

app = Flask(__name__)

data = []


@app.route("/")
def main():
    return "Welcome!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
