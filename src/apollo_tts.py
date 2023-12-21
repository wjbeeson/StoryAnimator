import json
import logging as log
import os.path
import time
from pathlib import Path
import ffmpeg
import apollo_config as config
import apollo_utils

from TTS.elevenlabs_speech_provider import ElevenLabsSpeechProvider
from TTS.google_speech_provider import GoogleSpeechProvider

g_google = GoogleSpeechProvider()
g_eleven = ElevenLabsSpeechProvider(config.ELEVENLABS_API_KEY_FILENAME)

g_production = {
    "Andy": (g_google, "en-US-Neural2-A"),
    "Benny": (g_google, "en-GB-Wavenet-B"),
    "Chandra": (g_google, "en-IN-Wavenet-C"),
    "Cora": (g_google, "en-US-Neural2-C"),
    "Dennis": (g_google, "en-US-Neural2-D"),
    "Faith": (g_google, "en-US-Neural2-F"),
    "Darshi": (g_google, "en-IN-Wavenet-D"),
    "Flora": (g_google, "en-GB-Wavenet-F"),
    "Grace": (g_google, "en-US-Neural2-G"),
    "Hanna": (g_google, "en-US-Neural2-H"),
    "Ian": (g_google, "en-US-Wavenet-I"),
    "Jacob": (g_google, "en-US-Neural2-J"),
    "Sarah": (g_google, "en-US-Studio-O"),
    "Talon": (g_google, "en-US-News-N"),
    "TheChad": (g_google, "en-US-Studio-M"),

    "Adam": (g_eleven, "Adam"),
    "Antoni": (g_eleven, "Antoni"),
    "Arnold": (g_eleven, "Arnold"),
    "Bella": (g_eleven, "Bella"),
    "Domi": (g_eleven, "Domi"),
    "Elli": (g_eleven, "Elli"),
    "Josh": (g_eleven, "Josh"),
    "Rachel": (g_eleven, "Rachel"),
    "Sam": (g_eleven, "Sam"),
    "Bruce": (g_eleven, "Bruce"),
    "Grandpa": (g_eleven, "Grandpa"),
    "Myra": (g_eleven, "Myra"),
    "Rakesh": (g_eleven, "Rakesh")
}

g_draft = {

    "Voice1": (g_google, "en-US-Standard-C"),
    "Voice2": (g_google, "en-US-Standard-B"),  # M
    "Voice3": (g_google, "en-US-Standard-E"),
    "Voice4": (g_google, "en-US-Standard-D"),  # M
    "Voice5": (g_google, "en-US-Standard-I"),  # M
    "Voice6": (g_google, "en-US-Standard-F"),
    "Voice7": (g_google, "en-US-Standard-G"),
    "Voice8": (g_google, "en-US-Standard-A"),  # M
    "Voice9": (g_google, "en-US-Standard-C"),
    "Voice10": (g_google, "en-US-Standard-B"),  # M
    "Voice11": (g_google, "en-US-Standard-E"),
    "Voice12": (g_google, "en-US-Standard-D"),  # M
    "Voice13": (g_google, "en-US-Standard-F")

}


def _lookup_provider(voice_name):
    if voice_name in g_production:
        return g_production[voice_name]
    else:
        # since there are new 11L voices being added to the library each day, make it easy to select
        # new ones.  assume any unrecognized voice is 11Labs
        return (g_eleven, voice_name)


def tts(meme_filename):
    log.info(f"Performing TTS on {meme_filename}")
    meme = json.load(open(str(meme_filename)))
    try:
        for i in range(len(meme["dialogue"])):
            dialogue = meme["dialogue"][str(i)]
            filename = apollo_utils.get_narration_filename(meme_filename, i)

            # to save some money, don't overwrite existing narrations.  user must manually delete in order
            # to regenerate them
            if os.path.exists(filename):
                log.info(f"Skipping existing narration file {filename}")
                continue

            provider, voice_id = _lookup_provider(
                dialogue["speakerID"]
            )

            # say the ssml text if specified, otherwise say the caption text.
            # note: this code will always write a narration .wav, even for blank text
            log.info(f"Performing TTS for: {filename}")
            provider.say(voice_id, dialogue["speak"], filename)

        audio_inputs = []
        for i in range(len(meme["dialogue"])):
            filename = apollo_utils.get_narration_filename(meme_filename, i)
            audio_inputs.append(ffmpeg.input(filename))
        (
            ffmpeg
            .concat(*audio_inputs, v=0, a=1)
            .output(str(Path(meme_filename).with_suffix(".wav")), loglevel="quiet")
            .run(overwrite_output=True)
        )
        meme["state"] = "TTS"
        meme["narrationFilepath"] = str(Path(meme_filename).with_suffix(".wav"))
        with open(str(meme_filename), "w") as f:
            f.write(json.dumps(meme))
        log.info(f"Narration successfully compiled")
        time.sleep(3)



    except Exception as x:
        log.exception("TTS failed")


#tts(r"C:\Users\wjbee\Desktop\Raptor\scripts\test.json")
