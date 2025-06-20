from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.cloud import speech
from google.genai import types
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
    prompt = ""
    if "prompt" not in request.files:
        return jsonify({"error": "No audio file sent"}), 400
    audioFile = request.files["prompt"]
    if audioFile == "":
        return jsonify({"error": "No audio file sent"}), 400
    
    speechClient = speech.SpeechClient()
    config = speech.RecognitionConfig(
        sample_rate_hertz=48000,
        language_code="en-US",
        model="latest_short",
        audio_channel_count=2,
    )
    audio = speech.RecognitionAudio(content=audioFile.read())
    
    operation = speechClient.long_running_recognize(config=config, audio=audio)
    print("Transcribing audio input...")
    response = operation.result(timeout=90)

    for i, result in enumerate(response.results):
        alternative = result.alternatives[0]
        print("-" * 20)
        print(f"First alternative of result {i}")
        print(f"Transcript: {alternative.transcript}")
        prompt = alternative.transcript

    question = f"Please answer the following prompt in less than five sentences: {prompt}."
    print(f"Question: {question}")
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

    print(f"Response: {response.text}")
    return jsonify({"Response": response.text})

@app.route("/photo", methods=["POST"])
def Photo():
    if "rawData" not in request.files:
        return jsonify({"error": "No image file sent"}), 400
    imageBytes = request.files["rawData"].read()
    if imageBytes == "":
        return jsonify({"error": "No image file sent"}), 400
    
    print(f"Image bytes: {imageBytes}")
    question = f"Describe the following image in less than five sentences."
    print(f"Question: {question}")
    client = genai.Client(vertexai=True, project="berkheiser-cis693", location="us-central1")

    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=[
            types.Part.from_bytes(
                data=imageBytes,
                mime_type='image/jpeg',
            ),
            question
        ],
        config=GenerateContentConfig(
            tools=[
                Tool(google_search=GoogleSearch())
            ],
        ),
    )

    print(f"Response: {response.text}")
    return jsonify({"Response": response.text})


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)