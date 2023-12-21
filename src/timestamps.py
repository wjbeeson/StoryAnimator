import string

from speechmatics.models import ConnectionSettings
from speechmatics.batch_client import BatchClient
from word import Word

import apollo_config as config


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
        print(f'job {job_id} submitted successfully, waiting for transcript')

        # Note that in production, you should set up notifications instead of polling.
        # Notifications are described here: https://docs.speechmatics.com/features-other/notifications
        transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
        # To see the full output, try setting transcription_format='json-v2'.
        print(transcript['results'])
        results = []
        for token in transcript['results']:
            if token['type'] == 'punctuation':
                continue
            results.append(token)
        return results


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
        print(f'job {job_id} submitted successfully, waiting for transcript')
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
        print(f'waiting for {job_id}...')
        transcript = client.wait_for_completion(job_id, transcription_format='json-v2')
        # To see the full output, try setting transcription_format='json-v2'.
        print(f'job {job_id} completed transcript successfully.')
        results = []
        for token in transcript['results']:
            if token['type'] == 'punctuation':
                continue
            results.append(token)
        return results



def check_if_match(detected_index, actual_index, detected_words, actual_words):
    # checking to make sure it's not the last word
    if detected_index >= len(detected_words) or actual_index >= len(actual_words):
        return True
    return detected_words[detected_index] == actual_words[actual_index]


def output_hardcoded_values(timestamps):
    words = []
    for word in timestamps:
        words.append([word.content, word.start_time, word.end_time])
    return str(words)


def input_hardcoded_values(timestamps_string):
    words = []
    object = eval(timestamps_string)
    for word in object:
        words.append(
            Word(
                word[0],
                word[1],
                word[2]
            )
        )
    return words
