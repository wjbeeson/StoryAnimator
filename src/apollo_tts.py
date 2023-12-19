import logging as log
import os.path

import re

import dto
import dto_utils
import apollo_config as config
from vulcan.elevenlabs_speech_provider import ElevenLabsSpeechProvider
from vulcan.google_speech_provider import GoogleSpeechProvider
from apollo_utils import get_narration_filename
from ContentElementFacade import ContentElementFacade, create_content_element_groups, combine_text_elements

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
    "Voice13" : (g_google, "en-US-Standard-F")

}


def _lookup_provider(voice_name, speaker_num, production):
    if production:
        if voice_name in g_production:
            return g_production[voice_name]
        else:
            # since there are new 11L voices being added to the library each day, make it easy to select
            # new ones.  assume any unrecognized voice is 11L
            return (g_eleven, voice_name )
    else:
        return g_draft[f"Voice{speaker_num}"]



def tts(meme_filename, production):
    log.info(f"Performing TTS on {meme_filename}")
    meme = dto_utils.dto_read(meme_filename)
    # form groups of adjacent text bubbles for same speaker within a panel
    groups = create_content_element_groups(meme)


    # create a line of narration for each group
    try:
        for panel_num, line_num, content_nums in groups:

            if len(content_nums) == 1:
                text = ContentElementFacade(meme, panel_num, content_nums[0]).speech_text
            else:
                text = combine_text_elements(meme, panel_num, content_nums)

            speaker_num = meme.panels[panel_num].content[content_nums[0]].speaker

            # for content elements like picture that don't have a speaker. an empty
            # narration file will be generated.  currently i use it as a placeholder
            # to simplify processing

            if not speaker_num:
                speaker_num = 1

            # <meme_filename>_<panel_num>_<narration_line_num>.wav
            filename = get_narration_filename(meme_filename, panel_num, line_num)

            # to save some money, don't overwrite existing narrations.  user must manually delete in order
            # to regenerate them
            if os.path.exists(filename):
                log.warning(f"Skipping existing narration file {filename}")
                continue

            provider, voice_id = _lookup_provider(
                meme.header.speakers.speaker[speaker_num - 1].voice,
                speaker_num,
                production)

            # say the ssml text if specified, otherwise say the caption text.
            # note: this code will always write a narration .wav, even for blank text
            if text.startswith("<speak>"):
                provider.say_ssml(voice_id, text, filename, rate=config.TTS_SPEAKING_RATE)
            else:
                provider.say(voice_id, text, filename, rate=config.TTS_SPEAKING_RATE)

            line_num += 1

        meme.header.state = dto.StateType.TTS
        meme.write(meme_filename, force=True)

    except Exception as x:
        log.exception("TTS failed")
