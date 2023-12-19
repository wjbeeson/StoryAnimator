import logging as log
import string
from string import punctuation

import numpy as np
import pandas as pd
from google.cloud import speech
from moviepy.editor import *

import apollo_config as config
import apollo_utils
import dto
from ContentElementFacade import ContentElementFacade, create_content_element_groups
from nw import nw, align, TimeStampNode

import timestamps as speechmatics

#
# 1. read the meme
# 2. for each message, open the corresponding .mp3
# 3. convert to temp.wav
# 4. perform STT - get timestamps
# 5. write the meme with timestamps
#
# note: probably need to perform some word matching.  if the # of timestamps
# doesn't match the Source text, then try to either throw away extras or interpolate the
# missing values.  Don't bother with this for the prototype though
#


g_client = speech.SpeechClient()
g_config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    enable_word_time_offsets=True,
    language_code="en-US",
    enable_automatic_punctuation=True,
    enable_spoken_emojis=True,
    model=config.ASR_SPEECH_MODEL,
    use_enhanced = config.ASR_USE_ENHANCED
)

def get_timestamps( filename ):
    print(f"Processing {filename}")

    with open(filename, 'rb') as audio_file:
        content = audio_file.read()
        audio = speech.RecognitionAudio(content=content)

    response = g_client.recognize(config=g_config, audio=audio)

    timestamps = []
    for result in response.results:
        alternative = result.alternatives[0]

        for word_info in alternative.words:
            timestamps.append(
                (word_info.start_time.total_seconds(),
                 apollo_utils.str_remove_any( word_info.word.casefold(),punctuation),
                 -1))  # correlated word index, TBD

    return timestamps

def _match_timestamps( asr_results, words ):

    last_match = 0
    for i, (t,word,l) in enumerate(asr_results):
        aligned = []
        for n in range(last_match,min(last_match+4,len(words))):
            if word == words[n]:
                asr_results[i] = (t,word,n)
                last_match = n
                break


def _align_timestamps( asr_results, words, duration ):
    _match_timestamps( asr_results, words )


    timestamps = [None] * len(words)
    for t, word, index in asr_results:
        if index != -1:
            timestamps[index] = t

    # fill gaps, 1st try
    for i,t in enumerate(timestamps):
        if t is None:
            for l, (t2, word, index) in enumerate(asr_results):
                if index == -1:
                    asr_results[l] = (t2,word,i)
                    timestamps[i]=t2
                    break

    # i'll be using pandas interpolate to fill gaps, which doesn't extrapolate the first
    # missing value
    if timestamps[0] is None:
        timestamps[0] = 0

    # it also doesn't extrapolate the last missing value, so add the duration adjusted by an
    # avg word length estimate
    timestamps.append(duration - .3)

    timestamps = pd.Series(timestamps).interpolate().to_list()
    timestamps = timestamps[:-1] # removing trailing timestamp

    assert None not in timestamps
    assert np.NaN not in timestamps

    return timestamps

def normalize_tokens( tokens ):

    normalized_tokens = []

    token : str
    for token in tokens:
        token = apollo_utils.str_remove_any(token,string.punctuation)
        if token:
            normalized_tokens += [token.casefold()]

    return normalized_tokens


def add_timestamps_to_meme( meme_filename ):
    meme : dto.Meme
    meme = dto.Meme.read(meme_filename)

    groups = create_content_element_groups(meme)
    raw_timestamps_list = []
    for panel_num, line_num, content_nums in groups:
        filename = apollo_utils.get_narration_filename(meme_filename, panel_num, line_num)
        raw_timestamps = speechmatics.get_timestamps_from_narration(filename)
        raw_timestamps_list.append(raw_timestamps)


    for panel_num, line_num, content_nums in groups:
        filename = apollo_utils.get_narration_filename(meme_filename, panel_num, line_num)

        # use expected representation: list of (time,word,_) tuples
        raw_timestamps = [(entry['start_time'], normalize_tokens( [entry['alternatives'][0]['content']] )[0], None) for entry in raw_timestamps]

        words = []
        timestamps = []
        for i,content_num in enumerate(content_nums):
            ce = ContentElementFacade(meme,panel_num,content_num)
            words += normalize_tokens(apollo_utils.get_tokens(ce.text))

        if ce.type != dto.ContentType.PICTURE:
            # need the narration duration to extrapolate missing timestamps
            duration = AudioFileClip(filename).duration

            # may compute v1 timestamps for debugging purposes
            # timestamps_v1 = _align_timestamps(raw_timestamps,words, duration)

            # align timestamps using NW algorithm
            tokens, nodes = nw(
                words,
                [TimeStampNode(word,timestamp) for timestamp,word,_ in raw_timestamps]
            )

            timestamps = align(tokens, nodes)

            # should be one timestamp for each word, not tokens (which was returned by nw)
            # because there could be '-' insertions
            assert len(timestamps)==len(words)

            for i, content_num in enumerate(content_nums):
                ce = ContentElementFacade(meme, panel_num, content_num)
                word_count = len(normalize_tokens(apollo_utils.get_tokens(ce.text)))
                ce.timestamps = timestamps[:word_count]
                timestamps = timestamps[word_count:]

                # if this content element is a member of group, set the duration to slightly
                # less than the next timestamp. this will simplify later code
                if i < len(content_nums) - 1 and timestamps:
                    ce.duration = timestamps[0] - .001
        else:
            timestamps = []

    return meme


def timestamp( meme_filename ):
    try:
        meme = add_timestamps_to_meme(meme_filename)
        meme.header.state = dto.StateType.TIMESTAMP
        meme.write(meme_filename, True)
    except Exception as x:
        log.exception("Word timestamp detection failed.")