#!/usr/bin/env python3

from datetime import datetime
import os
import requests

url = "https://berkheiser-cis693.uk.r.appspot.com/prompt"

date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

os.system(f'arecord -D hw:0,0 --format S16_LE --duration=5 --rate 48000 -c2 /home/joseberk/CIS693-MastersProject/testSounds/{date}.wav')

files = {"prompt": open(f'/home/joseberk/CIS693-MastersProject/testSounds/{date}.wav', 'rb')}
response = requests.post(url, files=files)
print(response.json()["Response"])

