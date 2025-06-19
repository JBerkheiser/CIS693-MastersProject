import pvporcupine
import subprocess
import numpy as np
import time


def get_next_audio_frame():
	rawBytes = process.stdout.read(frameLength * bytesPerSample * channels)
	samples = np.frombuffer(rawBytes, dtype=np.int16)
	rightChannel = samples[1::2]
	return rightChannel

keyWord1Path = "/home/joseberk/CIS693-MastersProject/includes/porcupine/Hey-Torkelson_en_raspberry-pi_v3_0_0.ppn"
keyWord2Path = "/home/joseberk/CIS693-MastersProject/includes/porcupine/jarvis_raspberry-pi.ppn"
file = open("/home/joseberk/CIS693-MastersProject/includes/porcupine/PorcupineAccessKey.txt", "r")
accessKey = file.read()
file.close()

bytesPerSample = 2
channels = 2
script = ""

while True:
	handle = pvporcupine.create(
		access_key=accessKey, 
		keyword_paths=[keyWord1Path, keyWord2Path],
		)
	frameLength = handle.frame_length
	process = subprocess.Popen(['arecord', '-D',  'hw:0,0', '-f', 'S16_LE', '-r', '16000', '-c', '2', '-t', 'raw'], stdout=subprocess.PIPE)
	while True:
		keywordIndex = handle.process(get_next_audio_frame())
		if keywordIndex == 0:
			print("Recording a query")
			script = "/home/joseberk/CIS693-MastersProject/source/frontend/CombinedTest.py"
			break
		elif keywordIndex == 1:
			print("Taking a photo")
			script = "/home/joseberk/CIS693-MastersProject/source/frontend/CameraTest.py"
	time.sleep(1)
	process.kill()
	subprocess.call(script)
	handle.delete()
