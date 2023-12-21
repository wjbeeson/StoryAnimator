import json
import logging as log
import string
from google.cloud import speech
from speechmatics.batch_client import BatchClient
from speechmatics.models import ConnectionSettings
import apollo_config as config
import apollo_utils
from dna_align import dna_align, align, TimeStampNode
from calculate_metadata import add_description, calculate_blocks

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
        job_id = submit_job(filename)
        ongoing_jobs_ids[job_id] = i
    for job_id in ongoing_jobs_ids:
        raw_timestamps = await_completion(job_id)
        raw_timestamps_list[ongoing_jobs_ids[job_id]] = raw_timestamps
    timestamps_list = []
    total_duration = 0
    for i in range(len(dialogue)):
        filename = apollo_utils.get_narration_filename(meme_filename, i)
        if i in list(finished_timestamps.keys()):
            log.info(
                f'Skipping existing timestamps {dialogue[str(i)]["speak"][0:min(50, len(dialogue[str(i)]["speak"]))]}')
            timestamps_list.extend(finished_timestamps[i])
        else:
            raw_timestamps = raw_timestamps_list[i]
            # use expected representation: list of (time,word,_) tuples
            raw_timestamps = [(entry['start_time'], normalize_tokens([entry['alternatives'][0]['content']])[0], None)
                              for entry in raw_timestamps]

            words = normalize_tokens(apollo_utils.get_tokens(dialogue[str(i)]["speak"]))

            # align timestamps using NW algorithm
            tokens, nodes = dna_align(
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
        with open(str(meme_filename), "w") as f:
            f.write(json.dumps(meme))

        add_description(meme_filename)

        meme = calculate_blocks(meme_filename)
        meme["state"] = "TIMESTAMPED"
        with open(str(meme_filename), "w") as f:
            f.write(json.dumps(meme))
    except Exception as x:
        log.exception("Word timestamp detection failed.")


def submit_job(audio_file):
    api_key = open(config.SPEECHMATICS_API_KEY_FILENAME).read()

    settings = ConnectionSettings(
        url="https://asr.api.speechmatics.com/v2",
        auth_token=api_key,
    )

    # Define transcription parameters
    conf = {
        "type": "transcription",
        "transcription_config": {
            "language": "en",
            "operating_point": "enhanced"
        }
    }
    # Open the client using a context manager
    with BatchClient(settings) as client:
        job_id = client.submit_job(
            audio=audio_file,
            transcription_config=conf,
        )
        log.info(f'job {job_id} submitted successfully, waiting for transcript')
        return job_id


def await_completion(job_id):
    api_key = open(config.SPEECHMATICS_API_KEY_FILENAME).read()

    settings = ConnectionSettings(
        url="https://asr.api.speechmatics.com/v2",
        auth_token=api_key,
    )

    # Open the client using a context manager
    with BatchClient(settings) as client:
        # Note that in production, you should set up notifications instead of polling.
        # Notifications are described here: https://docs.speechmatics.com/features-other/notifications
        log.info(f'waiting for {job_id}...')
        transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
        # To see the full output, try setting transcription_format='json-v2'.
        log.info(f'job {job_id} completed transcript successfully.')
        results = []
        for token in transcript['results']:
            if token['type'] == 'punctuation':
                continue
            results.append(token)
        return results


def get_timestamps_from_narration(audio_file):
    api_key = open(config.SPEECHMATICS_API_KEY_FILENAME).read()

    settings = ConnectionSettings(
        url="https://asr.api.speechmatics.com/v2",
        auth_token=api_key,
    )

    # Define transcription parameters
    conf = {
        "type": "transcription",
        "transcription_config": {
            "language": "en",
            "operating_point": "enhanced"
        }
    }
    # Open the client using a context manager
    with BatchClient(settings) as client:

        job_id = client.submit_job(
            audio=audio_file,
            transcription_config=conf,
        )
        log.info(f'job {job_id} submitted successfully, waiting for transcript')

        # Note that in production, you should set up notifications instead of polling.
        # Notifications are described here: https://docs.speechmatics.com/features-other/notifications
        transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
        # To see the full output, try setting transcription_format='json-v2'.
        log.info(transcript['results'])
        results = []
        for token in transcript['results']:
            if token['type'] == 'punctuation':
                continue
            results.append(token)
        return results
