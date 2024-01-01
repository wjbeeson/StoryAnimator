import random
import re
from pathlib import Path
import ffmpeg
import string

def select_random_element(l):
    return l[random.randrange(0, len(l))]


def get_narration_filename(meme_filename, index):
    meme_filepath = Path(meme_filename)
    filename = str(meme_filepath.parent) + "\\" + str(meme_filepath.stem) + f"_{index}.wav"
    return filename


def get_word_list(text, tokens=True):
    # Replace troublesome characters
    text = text.replace("’", "'")

    # Define characters to split on
    whitespace_chars = "\n\t "

    # Define characters to keep
    allowed_punctuation = '^″‶?.,"!\-:;\'’`\(\)\/\[\]'
    if tokens:
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = text.lower()

    # Perform regex split
    regex = f"[-+*•\w{allowed_punctuation}]+|[{whitespace_chars}]+"
    words = []
    for word in re.findall(regex, text):
        if word[0] not in whitespace_chars:

            # check for punctuation island
            if re.search('[a-zA-Z]', word) is None and re.search('\d+', word) is None:
                if len(words) > 0:
                    words[-1] += word
            else:

                # add space at end of word if not a token
                if not tokens:
                    word += " "
                words.append(word)
    return words

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
