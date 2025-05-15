from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.genai.types import (
    GenerateContentConfig,
    GoogleSearch,
    HttpOptions,
    Tool,
)

app = Flask(__name__)
CORS(app)

@app.route("/prompt", methods=["POST"])
def Prompt():
    if "prompt" not in request.get_json():
        return jsonify({"error": "No prompt sent"}), 400
    prompt = request.get_json().get("prompt", "")
    if prompt == "":
        return jsonify({"error": "No prompt sent"}), 400

    question = f"Please answer the following prompt in less than five sentences: {prompt}."
    client = genai.Client(vertexai=True, project="berkheiser-cis693", location="us-central1")

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=question,
        config=GenerateContentConfig(
            tools=[
                Tool(google_search=GoogleSearch())
            ],
        ),
    )
    return jsonify({"Response": response.text})


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)