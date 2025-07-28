from resemble import Resemble
import requests

api_token = ''
Resemble.api_key(api_token)

response = Resemble.v2.clips.create_sync(
    project_uuid='89e0ea27',
    voice_uuid='55592656',
    body='This is a test of the text to speech software',
    is_archived=None,
    title=None,
    sample_rate=None,
    output_format=None,
    precision=None,
    include_timestamps=None,
    raw=None
)


if response['success']:
    output_path = "output.wav"
    clip = response['item']
    clip_uuid = clip['uuid']
    clip_url = clip['audio_src']
    print(f"Response was successful! Sound has been created with UUID {clip_uuid}.")
    audio = requests.get(clip_url)
    if audio.ok:
        with open(output_path, "wb") as f:
            f.write(audio.content)
        print(f"Audio downloaded and saved as {output_path}")
    else:
        print("Failed to download audio:", audio.status_code)
else:
    print("Response was unsuccessful!")

    # In case of an error, print the error to STDOUT
    print(response)