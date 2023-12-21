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
import json
import timestamps as speechmatics
from pathlib import Path

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
    use_enhanced=config.ASR_USE_ENHANCED
)


def normalize_tokens(tokens):
    normalized_tokens = []

    token: str
    for token in tokens:
        token = apollo_utils.str_remove_any(token, string.punctuation)
        if token:
            normalized_tokens += [token.casefold()]

    return normalized_tokens


def add_timestamps_to_meme(meme_filename):
    meme = json.load(open(str(meme_filename)))
    dialogue = meme["dialogue"]
    finished_timestamps = {}
    ongoing_jobs_ids = {}
    raw_timestamps_list = {}
    for i in range(len(dialogue)):
        filename = apollo_utils.get_narration_filename(meme_filename, i)
        if "timestamps" in dialogue[str(i)]:
            if dialogue[str(i)]["timestamps"] is not None:
                if len(dialogue[str(i)]["timestamps"]) > 0:
                    finished_timestamps[i] = dialogue[str(i)]["timestamps"]
                    continue
        job_id = speechmatics.submit_job(filename)
        ongoing_jobs_ids[job_id] = i
    for job_id in ongoing_jobs_ids:
        raw_timestamps = speechmatics.await_completion(job_id)
        raw_timestamps_list[ongoing_jobs_ids[job_id]] = raw_timestamps
    timestamps_list = []
    total_duration = 0
    for i in range(len(dialogue)):
        filename = apollo_utils.get_narration_filename(meme_filename, i)
        if i in list(finished_timestamps.keys()):
            log.warning(
                f'Skipping existing timestamps {dialogue[str(i)]["speak"][0:min(50, len(dialogue[str(i)]["speak"]))]}')
            timestamps_list.extend(finished_timestamps[i])
        else:
            raw_timestamps = raw_timestamps_list[i]
            # use expected representation: list of (time,word,_) tuples
            raw_timestamps = [(entry['start_time'], normalize_tokens([entry['alternatives'][0]['content']])[0], None)
                              for entry in raw_timestamps]

            words = normalize_tokens(apollo_utils.get_tokens(dialogue[str(i)]["speak"]))

            # align timestamps using NW algorithm
            tokens, nodes = nw(
                words,
                [TimeStampNode(word, ts) for ts, word, _ in raw_timestamps]
            )

            timestamps = align(tokens, nodes)
            for j, ts in enumerate(timestamps):
                timestamps[j] = round((ts + total_duration), 2)

            timestamps_list.extend(timestamps)
            # should be one timestamp for each word, not tokens (which was returned by nw)
            # because there could be '-' insertions
            assert len(timestamps) == len(words)
            dialogue[str(i)]["timestamps"] = timestamps
            with open(str(meme_filename), "w") as f:
                f.write(json.dumps(meme))
        total_duration += apollo_utils.probe_audio(filename)
    meme["timestamps"] = timestamps_list
    return meme


def timestamp(meme_filename):
    try:
        meme = add_timestamps_to_meme(meme_filename)
        meme["state"] = "TIMESTAMPED"
        with open(str(meme_filename), "w") as f:
            f.write(json.dumps(meme))
    except Exception as x:
        log.exception("Word timestamp detection failed.")


timestamp(r"C:\Users\wjbee\Desktop\Raptor\scripts\test.json")
