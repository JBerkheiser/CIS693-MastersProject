#!/usr/bin/env python3

from datetime import datetime
import os
import requests

url = "https://berkheiser-cis693.uk.r.appspot.com/prompt"

date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
os.system(f'rpicam-jpeg --output /home/joseberk/CIS693-MastersProject/testPics/{date}.jpg')

files = {"photo": open(f'/home/joseberk/CIS693-MastersProject/testPics/{date}.jpg', 'rb')}
print("Done")
# response = requests.post(url, files=files)
# print(response.json()["Response"])