#!/usr/bin/env python3

from datetime import datetime
import os
import requests
import wave
import base64

def decodeAudio(encodedAudio):
    PCMBytes = base64.b64decode(encodedAudio)
    with wave.open("/home/joseberk/CIS693-MastersProject/testResponseAudio/response.wav", "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(PCMBytes)


url = "https://berkheiser-cis693.uk.r.appspot.com/prompt"
date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
os.system(f'arecord -D hw:0,0 --format S16_LE --duration=3 --rate 48000 -c2 /home/joseberk/CIS693-MastersProject/testSounds/{date}.wav')

files = {"prompt": open(f'/home/joseberk/CIS693-MastersProject/testSounds/{date}.wav', 'rb')}
response = requests.post(url, files=files)
print(response.json()["textResponse"])
decodeAudio(response.json()["audioResponse"])
os.system('aplay -D hw:0,0 -c2 /home/joseberk/CIS693-MastersProject/testResponseAudio/response.wav')


