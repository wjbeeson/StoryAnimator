import pathlib
import string

import pandas as pd
import statistics
import numpy as np
import re
import ffmpeg
# opencv-python
import cv2
import xml.etree.ElementTree as XmlElementTree
import io

from string import punctuation

import random

from pathlib import Path


def select_random_element(l):
    return l[random.randrange(0,len(l))]
def get_narration_filename(meme_filename, index):
    meme_filepath = Path(meme_filename)
    filename = str(meme_filepath.parent) + "\\" + str(meme_filepath.stem) + f"_{index}.wav"
    return filename


def str_remove_any(s, chars_to_remove):
    return s.translate({ord(i): None for i in chars_to_remove})



WHITESPACE_CHARS = "\n\t "

def split_keep_spaces(text):
    def unwanted_chars(variable):
        letters = [' ', '\n', '\t']
        if (variable in letters and len(variable) == 1):
            return False
        else:
            return True
    split = re.split(r'(?<=[\ ])\s*', text)
    remove_empty = list(filter(None, split))
    remove_spaces = list(filter(unwanted_chars, remove_empty))
    return remove_spaces


def get_tokens(text, discard_ws = True):
    text = text.replace("’","'")
    """
    Parses text into a list of word tokens and whitespace tokens
    Returns
    -------

    """
    punctuation = '^″‶?.,"!\-:;\'’`\(\)\/'
    regex = f"[-+*•\w{punctuation}]+|[{WHITESPACE_CHARS}]+"
    return [ word for word in re.findall(regex, text) if not discard_ws or word[0] not in WHITESPACE_CHARS]




def strip_ws(text):
    return " ".join(get_tokens(text))

def count_word_tokens( token_list ):
    return len([token for token in token_list if token[0] not in WHITESPACE_CHARS])

def count_words( text ):
    return count_word_tokens(get_tokens(text))

def probe_video(video_path):
    probe = ffmpeg.probe(video_path)
    stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    if stream is None:
        raise Exception(f"File: {video_path} is not a valid file, and is likely corrupted.")
    duration = float(stream['duration'])

    fps_raw = stream['avg_frame_rate']
    fps_split = fps_raw.split("/")
    fps = float(int(fps_split[0]) / int(fps_split[1]))

    video_width = int(stream['width'])

    video_height = int(stream['height'])

    return (duration, fps, video_width, video_height)


def probe_audio(audio_file):
    probe = ffmpeg.probe(audio_file)
    stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = float(stream['duration'])
    return (duration)

pass