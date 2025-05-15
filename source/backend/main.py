from flask import Flask, jsonify, request
from flask_cors import CORS
from vertexai.generative_models import GenerativeModel
app = Flask(__name__)
CORS(app)

@app.route("/prompt", methods=["POST"])
def Prompt():
    if "prompt" not in request.get_json():
        return jsonify({"error": "No prompt sent"}), 400
    prompt = request.get_json()
    if prompt == "":
        return jsonify({"error": "No prompt sent"}), 400

    model = GenerativeModel("gemini-2.5-pro-exp-03-25")
    request = f"Please answer the following prompt in less than five sentences: ${prompt}."
    response = model.generate_content([request])
    return jsonify({"Response": response.text})


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)