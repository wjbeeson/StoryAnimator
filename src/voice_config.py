from TTS.elevenlabs_speech_provider import ElevenLabsSpeechProvider
from TTS.google_speech_provider import GoogleSpeechProvider
import apollo_config as config

g_google = GoogleSpeechProvider()
g_eleven = ElevenLabsSpeechProvider(config.ELEVENLABS_API_KEY_FILENAME)


class VoiceConfig:
    def __init__(self, rate=None, volume=None, pitch=None):
        self.rate = rate
        self.volume = volume
        self.pitch = pitch


predefined_voices = {
    "Andy": (g_google, "en-US-Neural2-A", VoiceConfig()),
    "Benny": (g_google, "en-GB-Wavenet-B", VoiceConfig()),
    "Chandra": (g_google, "en-IN-Wavenet-C", VoiceConfig()),
    "Cora": (g_google, "en-US-Neural2-C", VoiceConfig()),
    "Darshi": (g_google, "en-IN-Wavenet-D", VoiceConfig()),
    "Dennis": (g_google, "en-US-Neural2-D", VoiceConfig()),
    "Faith": (g_google, "en-US-Neural2-F", VoiceConfig()),
    "Flora": (g_google, "en-GB-Wavenet-F", VoiceConfig()),
    "Grace": (g_google, "en-US-Neural2-G", VoiceConfig()),
    "Hanna": (g_google, "en-US-Neural2-H", VoiceConfig()),
    "Ian": (g_google, "en-US-Wavenet-I", VoiceConfig()),
    "Jacob": (g_google, "en-US-Neural2-J", VoiceConfig()),
    "Talon": (g_google, "en-US-News-N", VoiceConfig()),

    "Sarah": (g_google, "en-US-Studio-O", VoiceConfig()),
    "Chad": (g_google, "en-US-Studio-M", VoiceConfig()),

    "David": (g_google, "en-US-Journey-D", VoiceConfig(rate=1.2, pitch=0.95)),
    "Jill": (g_google, "en-US-Journey-F", VoiceConfig()),

    "Adam": (g_eleven, "Adam", VoiceConfig()),
    "Antoni": (g_eleven, "Antoni", VoiceConfig()),
    "Arnold": (g_eleven, "Arnold", VoiceConfig()),
    "Bella": (g_eleven, "Bella", VoiceConfig()),
    "Bruce": (g_eleven, "Bruce", VoiceConfig()),
    "Domi": (g_eleven, "Domi", VoiceConfig()),
    "Elli": (g_eleven, "Elli", VoiceConfig()),
    "Josh": (g_eleven, "Josh", VoiceConfig()),
    "Rachel": (g_eleven, "Rachel", VoiceConfig()),
    "Sam": (g_eleven, "Sam", VoiceConfig()),
    "Grandpa": (g_eleven, "Grandpa", VoiceConfig()),
    "Myra": (g_eleven, "Myra", VoiceConfig()),
    "Rakesh": (g_eleven, "Rakesh", VoiceConfig()),
    "Natasha": (g_eleven, "Natasha", VoiceConfig()),
    "Jayce": (g_eleven, "Jayce", VoiceConfig())
}
