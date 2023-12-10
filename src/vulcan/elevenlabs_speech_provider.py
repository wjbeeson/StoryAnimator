import re

from vulcan.speech_provider import ISpeechProvider
from elevenlabslib import *
from elevenlabslib.helpers import *


class ElevenLabsSpeechProvider(ISpeechProvider ):
    def __init__(self, key_filename ):
        with open(key_filename,'r') as f: key=f.read()
        self._user = ElevenLabsUser(key)

    def say_ssml(self, voice, ssml, filename, rate=1.0):
        # 11 doesn't support ssml yet.  but this might not actually be ssml - it also could be
        # unformatted text that was placed in the speak element

        text = ssml.replace("<speak>", "").replace("</speak>", "")

        self.say( voice,text, filename, rate)
    def say(self, voice, text, filename, rate=1.0):
        voices = self._user.get_voices_by_name(voice)

        # when this proves to no longer be the case, we shall require a different selection mechanism
        assert len(voices)==1

        # todo: 11 supports a few other parameters like stabiliy and similiarity.  we may wish to explore these
        # in the future
        wav_data = voices[0].generate_audio_bytes(text,
                                                  model_id= "eleven_multilingual_v2")
        save_audio_bytes(wav_data, filename, "wav")