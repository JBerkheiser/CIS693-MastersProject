#!/usr/bin/env python3

from datetime import datetime
import os
import requests
import wave
import base64

def getAudio(audioURL, date):
    output_path = f"/home/joseberk/CIS693-MastersProject/testResponseAudio/{date}.wav"
    audio = requests.get(audioURL)
    if audio.ok:
        with open(output_path, "wb") as f:
            f.write(audio.content)
        print(f"Audio downloaded and saved as {output_path}")
    else:
        print("Failed to download audio:", audio.status_code)


url = "https://berkheiser-cis693.uk.r.appspot.com/prompt"
date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
os.system(f'arecord -D hw:0,0 --format S16_LE --duration=5 --rate 48000 -c2 /home/joseberk/CIS693-MastersProject/testSounds/{date}.wav')

files = {"prompt": open(f'/home/joseberk/CIS693-MastersProject/testSounds/{date}.wav', 'rb')}
response = requests.post(url, files=files)
print(response.json()["textResponse"])
getAudio(response.json()["audioResponse"], date)
os.system(f'ffmpeg -i /home/joseberk/CIS693-MastersProject/testResponseAudio/{date}.wav -ar 44100 -ac 2 -sample_fmt s16 /home/joseberk/CIS693-MastersProject/testResponseAudio/playableAudio.wav')
os.system(f'aplay -D hw:0,0 -c2 /home/joseberk/CIS693-MastersProject/testResponseAudio/playableAudio.wav')


