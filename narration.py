import uuid

from elevenlabs import generate, play, set_api_key, save
from timestamps import *

import wave
import contextlib
from gcloud import storage
from oauth2client.service_account import ServiceAccountCredentials
from utility import *
elevenlabs_api_key = open("keys/elevenlabs").read()


def generate_narration_file(script, speaker, version):
    narration_file = f"temp/{uuid.uuid4()}.wav"
    #script_file = f"temp/{uuid.uuid4()}.txt"

    set_api_key(elevenlabs_api_key)
    audio = generate(
        text=script,
        voice=speaker,
        model=version
    )
    # play(audio)
    save(audio, narration_file)
    #with open(script_file, 'w') as f:
    #    f.write(script)
    # TODO Delete temp file after upload

    # upload to google cloud bucket
    #narration_url = upload_file_to_google(narration_file)
    #script_url = upload_file_to_google(script_file)

    print(f"Generated Narration for {speaker}: {script}")
    return narration_file

