from vulcan.speech_provider import ISpeechProvider
from google.cloud import texttospeech


class GoogleSpeechProvider(ISpeechProvider ):
    def __init__(self ):
        self._client = texttospeech.TextToSpeechClient()

    def _say(self, filename, voice, input, rate):
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=rate
        )

        response = self._client.synthesize_speech(
            input=input, voice=voice, audio_config=audio_config
        )

        with open(filename,'wb') as f:  f.write(response.audio_content)

    def say_ssml(self, voice, ssml_text, filename, rate=1.0):
        self._say(filename, voice, texttospeech.SynthesisInput(ssml=ssml_text), rate)

    def say(self, voice, text, filename, rate=1.0):
        self._say(filename, voice, texttospeech.SynthesisInput(text=text),rate)


