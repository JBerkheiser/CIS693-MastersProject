from gpiozero import Button
import os

button = Button(27)
button.wait_for_press()
print("The button was pressed")