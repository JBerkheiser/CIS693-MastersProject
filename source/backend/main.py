from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/hello", methods=["GET"])
def hello():
    return jsonify(message="hello world")


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)