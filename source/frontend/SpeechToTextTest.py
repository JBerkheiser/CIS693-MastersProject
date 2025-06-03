import requests

File = "C:/School/CIS693-MastersProject/testSounds/03-06-2025_09-35-35.wav"
url = "https://berkheiser-cis693.uk.r.appspot.com/prompt"

files = {"prompt": open(File, 'rb')}
response = requests.post(url, files=files)
print(response)

