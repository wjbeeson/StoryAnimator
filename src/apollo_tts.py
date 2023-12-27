import json
import logging as log
import os.path
import shutil
import time
from pathlib import Path
import ffmpeg
from scipy.io import wavfile

from voice_config import predefined_voices, g_google, g_eleven
import apollo_utils

from voice_config import VoiceConfig
from scipy.io.wavfile import read as read_wav
from pydub import AudioSegment
import noisereduce as nr


def _lookup_provider(voice_name):
    if voice_name.title() in predefined_voices:
        return predefined_voices[voice_name.title()]
    else:
        # since there are new 11L voices being added to the library each day, make it easy to select
        # new ones.  assume any unrecognized voice is 11Labs
        return (g_eleven, voice_name.title(), None)


def postprocess_narration(filename, voice_config):
    temp_filename = str(Path(filename).parent) + "\\temp.wav"
    if voice_config is None:
        voice_config = VoiceConfig()
    if voice_config.rate is not None:
        ffmpeg.input(filename).filter("atempo", voice_config.rate).output(temp_filename).run(overwrite_output=True,
                                                                                             quiet=True)
        shutil.move(temp_filename, filename)
    if voice_config.volume is not None:
        ffmpeg.input(filename).filter("volume", voice_config.volume).output(temp_filename).run(overwrite_output=True,
                                                                                               quiet=True)
        shutil.move(temp_filename, filename)
    if voice_config.pitch is not None:
        sampling_rate, _ = read_wav(filename)
        (
            ffmpeg.input(filename)
            .filter("asetrate", sampling_rate * voice_config.pitch)
            .filter("aresample", sampling_rate)
            .filter("atempo", 1 / voice_config.pitch)
            .output(temp_filename)
            .run(overwrite_output=True, quiet=True)
        )
        shutil.move(temp_filename, filename)
    if voice_config.eop_delay is not None:
        silent_audio = AudioSegment.silent(duration=voice_config.eop_delay * 1000)  # duration in milliseconds
        audio = AudioSegment.from_wav(filename)
        concat = audio + silent_audio
        concat.export(temp_filename, format="wav")
        shutil.move(temp_filename, filename)
    rate, data = wavfile.read(str(Path(filename).with_suffix(".wav")))
    reduced_noise = nr.reduce_noise(y=data, sr=rate)
    wavfile.write("mywav_reduced_noise.wav", rate, reduced_noise)


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
                log.info(f"Skipping existing narration file {str(Path(filename).name)}")
                continue
            provider, voice_id, voice_config = _lookup_provider(
                dialogue["speakerID"]
            )

            # say the ssml text if specified, otherwise say the caption text.
            # note: this code will always write a narration .wav, even for blank text
            log.info(f"Performing TTS for: {str(Path(filename).name)}")
            provider.say(voice_id, dialogue["speak"], filename)
            postprocess_narration(filename, voice_config)

        audio_inputs = []
        for i in range(len(meme["dialogue"])):
            filename = apollo_utils.get_narration_filename(meme_filename, i)
            audio_inputs.append(ffmpeg.input(filename))
        (
            ffmpeg
            .concat(*audio_inputs, v=0, a=1)
            .output(str(Path(meme_filename).with_suffix(".wav")), loglevel="quiet")
            .run(overwrite_output=True, quiet=True)
        )

        meme["state"] = "TTS"
        meme["narrationFilename"] = str(Path(meme_filename).with_suffix(".wav").name)
        meme["duration"] = apollo_utils.probe_audio(str(Path(meme_filename).with_suffix(".wav"))) + 2
        with open(str(meme_filename), "w") as f:
            f.write(json.dumps(meme))
        log.info(f"Narration successfully compiled")

    except Exception as x:
        log.exception("TTS failed")

pass
#tts(r"C:\Users\wjbee\Desktop\Raptor\scripts\12.26.2023\Mustard_Blowup.json")
