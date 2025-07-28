from gpiozero import Button
from datetime import datetime
import os

button = Button(27)
button.wait_for_press()
date = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
print("The button was pressed, recording")
os.system(f'arecord -D hw:0,0 --format S16_LE --duration=5 --rate 48000 -c2 /home/joseberk/CIS693-MastersProject/testSounds/{date}.wav')
