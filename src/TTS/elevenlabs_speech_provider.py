from TTS.speech_provider import ISpeechProvider
from elevenlabs import Voice, VoiceSettings, generate, set_api_key, save, voices


class ElevenLabsSpeechProvider(ISpeechProvider):
    def __init__(self, key_filename):
        with open(key_filename, 'r') as f: key = f.read()
        set_api_key(key)

    def say(self, voice, text, filename, model):
        if model is None:
            model = "eleven_multilingual_v2"
        voice_id = ""
        for voice_obj in voices():
            if voice_obj.name == voice:
                voice_id = voice_obj.voice_id
                break
        if voice_id == "":
            raise Exception(f"Voice not found: {voice}")
        audio = generate(
            text=text,
            model=model,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(stability=0.71, similarity_boost=0.5, style=0.0, use_speaker_boost=True)
            )
        )
        save(audio, filename)


#ElevenLabsSpeechProvider(r"C:\Users\wjbee\PycharmProjects\Raptor\config\11labs.key").say("Jayce", "Before you put on a frown, make completely sure there are no smiles available.", "test.wav", "eleven_multilingual_v1")