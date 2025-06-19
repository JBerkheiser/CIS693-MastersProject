#!/usr/bin/env python3

from datetime import datetime
import os
import requests

url = "https://berkheiser-cis693.uk.r.appspot.com/photo"

date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
os.system(f'rpicam-jpeg --output /home/joseberk/CIS693-MastersProject/testPics/{date}.jpeg')

files = {"rawData": open(f'/home/joseberk/CIS693-MastersProject/testPics/{date}.jpeg', 'rb')}
print("Done")
response = requests.post(url, files=files)
print(response.json()["Response"])
