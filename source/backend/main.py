from flask import Flask, jsonify, request
from flask_cors import CORS
from google import genai
from google.cloud import speech
from google.cloud import secretmanager
from google.genai import types
from google.genai.types import (
    GenerateContentConfig,
    SpeechConfig,
    VoiceConfig,
    GoogleSearch,
    HttpOptions,
    Tool,
)
import base64
from resemble import Resemble
import google_crc32c

app = Flask(__name__)
CORS(app)

def accessSecretVersion(projectID, secretID, versionID) -> secretmanager.AccessSecretVersionResponse:
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{projectID}/secrets/{secretID}/versions/{versionID}"

    response = client.access_secret_version(request={"name":name})

    crc32c = google_crc32c.Checksum()
    crc32c.update(response.payload.data)
    if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
        print("Data corruption detected.")
        return response

    payload = response.payload.data.decode("UTF-8")
    return payload

def convertAudioToText(audioFile):
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
        print(f"Transcript: {alternative.transcript}")
        prompt = alternative.transcript
    return prompt

def convertTextToAudio(textResponse):
    api_token = accessSecretVersion("848154742223", "TextToSpeechAPIKey", "1")
    Resemble.api_key(api_token)

    response = Resemble.v2.clips.create_sync(
        project_uuid='89e0ea27',
        voice_uuid='55592656',
        body=textResponse,
        is_archived=None,
        title=None,
        sample_rate=None,
        output_format=None,
        precision=None,
        include_timestamps=None,
        raw=None
    )
    return response['item']['audio_src']

def answerPrompt(prompt):
    question = f"Please answer the following prompt in less than five sentences, and with only alpha-numeric characters and periods: {prompt}."
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
    return response

def describeImage(imageBytes):
    question = f"Describe the following image in less than five sentences, and with only alpha-numeric characters and periods."

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
    return response


@app.route("/prompt", methods=["POST"])
def Prompt():
    prompt = ""
    if "prompt" not in request.files:
        return jsonify({"error": "No audio file sent"}), 400
    audioFile = request.files["prompt"]
    if audioFile == "":
        return jsonify({"error": "No audio file sent"}), 400

    response = answerPrompt(convertAudioToText(audioFile))

    audioURL = convertTextToAudio(response.text)
    return jsonify({"textResponse": response.text, "audioResponse": audioURL})

@app.route("/photo", methods=["POST"])
def Photo():
    if "rawData" not in request.files:
        return jsonify({"error": "No image file sent"}), 400
    imageBytes = request.files["rawData"].read()
    if imageBytes == "":
        return jsonify({"error": "No image file sent"}), 400
    
    response = describeImage(imageBytes)
    
    audioURL = convertTextToAudio(response.text)
    return jsonify({"textResponse": response.text, "audioResponse": audioURL})


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)