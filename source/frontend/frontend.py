###############################################################
# Title: frontend.py
# Author: Joe Berkheiser
# Date Created: 23 July 2025
# Description: This code is the frontend for my CIS 693 
#   project.  It waits for a given wake word, records the 
#   following audio, and communicates with the backend to get
#   a response.
#
# Known Issues:
# - No retries if audio/photo fails
# - Wake word can falsely trigger
###############################################################

###############################################################
# IMPORTS
###############################################################
import os
import time
import subprocess
from enum import Enum
from datetime import datetime

import numpy as np
import pvporcupine
import requests

###############################################################
# CONSTANTS
###############################################################
PROJECT_PATH = "/home/joseberk/CIS693-MastersProject"

HARDWARE = "hw:0,0"
INPUT_FORMAT = "S16_LE"
INPUT_RATE = "48000"
RECORD_DURATION = "5"

OUTPUT_CHANNELS = "2"
OUTPUT_RATE = "44100"
OUTPUT_FORMAT = "s16"

VOICE_PROMPT_KEYWORD = f"{PROJECT_PATH}/includes/porcupine/Hey-Torkelson_en_raspberry-pi_v3_0_0.ppn"
PHOTO_PROMPT_KEYWORD = f"{PROJECT_PATH}/includes/porcupine/jarvis_raspberry-pi.ppn"
PORCUPINE_ACCESS_KEY_PATH = f"{PROJECT_PATH}/includes/porcupine/PorcupineAccessKey.txt"
CLOUD_ENDPOINT_URL = "https://berkheiser-cis693.uk.r.appspot.com/"
RECORD_COMMAND = f"arecord -D {HARDWARE} --format {INPUT_FORMAT} --duration {RECORD_DURATION} --rate {INPUT_RATE} -c2 {PROJECT_PATH}/testSounds/"
CONVERT_COMMAND_INPUT = f"ffmpeg -i {PROJECT_PATH}/testResponseAudio/"
CONVERT_COMMAND_OUTPUT = f"-ar {OUTPUT_RATE} -ac {OUTPUT_CHANNELS} -sample_fmt {OUTPUT_FORMAT} {PROJECT_PATH}/testResponseAudio/"
PLAYBACK_COMMAND = f"aplay -D {HARDWARE} -c2 {PROJECT_PATH}/testResponseAudio/"
PHOTO_COMMAND = f"rpicam-jpeg --output {PROJECT_PATH}/testPics/"

###############################################################
# ENUMS
###############################################################
class States(Enum):
    WAKE_WORD = 0
    QUERY_PROMPT = 1
    PHOTO_PROMPT = 2
    RESPOND = 3
    ERROR = 4

###############################################################
# FUNCTIONS
###############################################################
def errorCatch(command: str, description: str) -> bool:
    ret = os.system(command)
    if ret != 0:
        print(f"[ERROR] {description} failed with exit code {ret}")
        return False
    return True

def downloadAudio(audioURL, date):
    output_path = f"{PROJECT_PATH}/testResponseAudio/{date}.wav"
    audio = requests.get(audioURL)
    if audio.ok:
        with open(output_path, "wb") as f:
            f.write(audio.content)
        print(f"Audio downloaded and saved as {output_path}")
    else:
        print("Failed to download audio:", audio.status_code)

def get_next_audio_frame(process, frameLength):
    bytesPerSample = 2
    channels = 2

    rawBytes = process.stdout.read(frameLength * bytesPerSample * channels)
    samples = np.frombuffer(rawBytes, dtype=np.int16)
    rightChannel = samples[1::2]

    return rightChannel

def waitForWakeWord():
    detectedWakeWord = "Error"
    with open(PORCUPINE_ACCESS_KEY_PATH, "r") as file:
        accessKey = file.read()

    handle = pvporcupine.create(
        access_key=accessKey, 
        keyword_paths=[VOICE_PROMPT_KEYWORD, PHOTO_PROMPT_KEYWORD],
    )
    frameLength = handle.frame_length

    process = subprocess.Popen(['arecord', '-D',  'hw:0,0', '-f', 'S16_LE', '-r', '16000', '-c', '2', '-t', 'raw'], stdout=subprocess.PIPE)
    
    while True:
        keywordIndex = handle.process(get_next_audio_frame(process, frameLength))
        if keywordIndex == 0:
            print("Query wake word detected, recording audio.")
            detectedWakeWord = "Query"
            break
        elif keywordIndex == 1:
            print("Photo wake word detected, taking a photo")
            detectedWakeWord = "Photo"
            break
        else:
            continue
    time.sleep(1)
    process.kill()
    handle.delete()
    return detectedWakeWord

###############################################################
# MAIN
###############################################################
def main():
    state = States.WAKE_WORD
    date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    url = ""
    dataPath = ""
    jsonHeader = ""

    while True:
        match state:
            case States.WAKE_WORD:
                print("CURRENT STATE: WAKE_WORD")
                match waitForWakeWord():
                    case "Query":
                        state = States.QUERY_PROMPT
                    case "Photo":
                        state = States.PHOTO_PROMPT
                    case "Error":
                        state = States.ERROR

            case States.QUERY_PROMPT:
                print("CURRENT STATE: QUERY_PROMPT")
                dataPath = f"{PROJECT_PATH}/testSounds/{date}.wav"
                if not errorCatch(f"{RECORD_COMMAND}{date}.wav", "Audio recording"):
                    state = States.ERROR
                    continue
                jsonHeader = "prompt"
                url = f"{CLOUD_ENDPOINT_URL}prompt"
                state = States.RESPOND

            case States.PHOTO_PROMPT:
                print("CURRENT STATE: PHOTO_PROMPT")
                dataPath = f"{PROJECT_PATH}/testPics/{date}.jpeg"
                if not errorCatch(f"{PHOTO_COMMAND}{date}.jpeg", "Photo capture"):
                    state = States.ERROR
                    continue
                jsonHeader = "rawData"
                url = f"{CLOUD_ENDPOINT_URL}photo"
                state = States.RESPOND

            case States.RESPOND:
                print("CURRENT STATE: RESPOND")
                try:
                    with open(dataPath, 'rb') as f:
                        files = {jsonHeader: f}
                        response = requests.post(url, files=files)
                        response.raise_for_status()

                        responseData = response.json()
                        print("Full Response JSON:", responseData)

                        if "textResponse" not in responseData or "audioResponse" not in responseData:
                            raise KeyError(f"Missing keys in response: {responseData.keys()}")

                        downloadAudio(responseData["audioResponse"], date)

                except requests.exceptions.RequestException as e:
                    print(f"[ERROR] HTTP request failed: {e}")
                    state = States.ERROR

                except KeyError as e:
                    print(f"[ERROR] Expected key missing from response: {e}")
                    state = States.ERROR

                except Exception as e:
                    print(f"[ERROR] Unexpected backend communication error: {e}")
                    state = States.ERROR
                
                if not errorCatch(f'{CONVERT_COMMAND_INPUT}{date}.wav {CONVERT_COMMAND_OUTPUT}{date}PLAYABLE.wav', "Audio conversion"):
                    state = States.ERROR
                    continue
                if not errorCatch(f'{PLAYBACK_COMMAND}{date}PLAYABLE.wav', "Audio playback"):
                    state = States.ERROR
                    continue

                state = States.WAKE_WORD

            case _:
                print("CURRENT STATE: ERROR")
                # Play Error Message
                state = States.WAKE_WORD
                continue

if __name__ == "__main__":
    main()
