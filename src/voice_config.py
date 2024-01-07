from TTS.elevenlabs_speech_provider import ElevenLabsSpeechProvider
from TTS.google_speech_provider import GoogleSpeechProvider
import apollo_config as config

g_google = GoogleSpeechProvider()
g_eleven = ElevenLabsSpeechProvider(config.ELEVENLABS_API_KEY_FILENAME)


class VoiceConfig:
    def __init__(self, rate=None, volume=None, pitch=None, eop_delay=None, model=None):
        self.rate = rate
        self.volume = volume
        self.pitch = pitch
        self.eop_delay = eop_delay
        self.model = model


predefined_voices = {
    "G_Studio_Female": (g_google, "en-US-Studio-O", VoiceConfig(rate=1.0, pitch=0.97)),
    "G_Studio_Male": (g_google, "en-US-Studio-M", VoiceConfig(rate=1.1)),

    "G_Journey_Male": (g_google, "en-US-Journey-D", VoiceConfig(rate=1.2, pitch=0.95)),
    "G_Journey_Female": (g_google, "en-US-Journey-F", VoiceConfig(rate=1.1, pitch=0.95, eop_delay=0.5)),

    "Jayce": (g_eleven, "Jayce", VoiceConfig(model="eleven_multilingual_v1"))
}
