import uuid

from elevenlabs import generate, play, set_api_key, save
from timestamps import *

import wave
import contextlib

elevenlabs_api_key = open("keys/elevenlabs").read()


def generate_narration_file(text, speaker, version):
    filename = f"temp/{uuid.uuid4()}"

    set_api_key(elevenlabs_api_key)
    audio = generate(
        text=text,
        voice=speaker,
        model=version
    )
    # play(audio)
    save(audio, f"{filename}.wav")

    #sound = AudioSegment.from_mp3(f"{filename}.mp3")
    #sound.export(f"{filename}.wav", format="wav")

    print(f"Generated Narration for {speaker}: {text}")
    return f"{filename}.wav"

