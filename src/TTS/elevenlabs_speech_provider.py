import re

import elevenlabs

from TTS.speech_provider import ISpeechProvider
from elevenlabs import Voice, VoiceSettings, generate, set_api_key, save, voices
from elevenlabslib.helpers import *


class ElevenLabsSpeechProvider(ISpeechProvider ):
    def __init__(self, key_filename ):
        with open(key_filename,'r') as f: key=f.read()
        set_api_key(key)
    def say(self, voice, text, filename, rate=1.0, pitch=0):
        voice_id = ""
        for voice_obj in voices():
            if voice_obj.name == voice:
                voice_id = voice_obj.voice_id
                break
        if voice_id == "":
            raise Exception(f"Voice not found: {voice}")
        audio = generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            )
        )
        save(audio, filename)