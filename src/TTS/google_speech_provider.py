from TTS.speech_provider import ISpeechProvider
from google.cloud import texttospeech


class GoogleSpeechProvider(ISpeechProvider):
    def __init__(self):
        self._client = texttospeech.TextToSpeechClient()

    def say(self, voice, text, filename, model=None):
        input_text = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(name=voice,language_code="en-US")
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        response = self._client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )
        with open(filename, 'wb') as f:  f.write(response.audio_content)