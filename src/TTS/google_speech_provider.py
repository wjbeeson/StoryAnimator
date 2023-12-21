from TTS.speech_provider import ISpeechProvider
from google.cloud import texttospeech


class GoogleSpeechProvider(ISpeechProvider):
    def __init__(self):
        self._client = texttospeech.TextToSpeechClient()

    def _say(self, filename, voice, input, rate, pitch):
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=rate,
            pitch=pitch
        )

        response = self._client.synthesize_speech(
            input=input, voice=voice, audio_config=audio_config
        )

        with open(filename, 'wb') as f:  f.write(response.audio_content)

    def say(self, voice, text, filename, rate=1.05, pitch=-7):
        # TODO: Figure out wtf is going on
        self._say(filename, voice, texttospeech.SynthesisInput(text=text), rate, pitch=-7)
