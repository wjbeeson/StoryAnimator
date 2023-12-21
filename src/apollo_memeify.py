import string

from apollo_utils import split_keep_spaces
import apollo_config as config
import logging as log
from pathlib import Path
import json
import re
# number of speaker elements to create
SPEAKER_COUNT = 4

def get_tag_contents(tag):
    tag = tag.replace("<", "").replace(">", "")
    tag_split = tag.split("=")
    tag_type = tag_split[0].translate(str.maketrans('', '', string.punctuation)).strip()
    tag_value = tag_split[1].translate(str.maketrans('', '', string.punctuation)).strip()
    return (tag_type, tag_value)


def find_tags(para, word_count, default_speaker_id="Talon", default_emotion="neutral"):
    speaker = default_speaker_id
    char_pos_emotions = {0: default_emotion}
    char_pos_headings = {}
    loop = True
    while loop:
        if para.find("<") != -1 and para.find(">") != -1:
            start = para.find("<")
            end = para.find(">")
            tag = para[start + 1:end]
            (tag_type, tag_value) = get_tag_contents(tag)
            match tag_type:
                case "speaker":
                    speaker = tag_value
                case "emotion":
                    char_pos_emotions[start] = tag_value
                case "heading":
                    char_pos_headings[start] = tag_value
                case _:
                    raise Exception(f"Unknown tag type {tag_type}")
            para = para[:start] + para[end + 1:]
        elif para.find("<") != -1 or para.find(">") != -1:
            raise Exception(f"Invalid tag: {para}")
        else:
            loop = False
    tokens = split_keep_spaces(para)

    word_pos_emotions = {}
    word_pos_headings = {}
    char_index = 0
    for i, token in enumerate(tokens):
        token_len = len(token)
        if len(char_pos_emotions) != 0:
            char_pos_emotion = list(char_pos_emotions.keys())[0]
            if char_index + token_len > char_pos_emotion:
                word_pos_emotions[i + word_count] = char_pos_emotions[char_pos_emotion]
                del char_pos_emotions[char_pos_emotion]

        if len(char_pos_headings) != 0:
            char_pos_heading = list(char_pos_headings.keys())[0]
            if char_index + token_len > char_pos_heading:
                word_pos_headings[i + word_count] = char_pos_headings[char_pos_heading]
                del char_pos_headings[char_pos_heading]
        char_index += token_len

    word_count += len(tokens)
    para_removed_tags = para
    return para_removed_tags, word_count, speaker, word_pos_emotions, word_pos_headings


def memeify(raw_filename, overwrite=False):
    #
    # create meme and header
    #
    log.info(f"Memeifying {raw_filename}")
    meme = json.load(open(str(config.APOLLO_PATH / "config/blank.json")))
    default_speaker_id = "Talon"
    #
    # create a caption element for each paragraph of the raw text
    #

    with open(raw_filename, "r", encoding="utf-8") as f:
        # split into paragraphs, dropping repeated linefeeds e.g. \n\n \n\n\n etc
        text = [para.replace('\n', ' ') for para in f.read().split('\n\n') if para != '']
    for i, para in enumerate(text):
        para = re.sub(' +', ' ', para)
        para = para.strip()
        para = para + " "
        text[i] = para

    # create caption content for each paragraph
    word_count = 0
    emotions = {}
    captions = []
    headings = {}
    speaker_id = default_speaker_id
    for i, para in enumerate(text):
        (
            para_removed_tags,
            word_count,
            speaker_id,
            para_emotions,
            para_headings
        ) = find_tags(
            para=para,
            word_count=word_count,
            default_speaker_id=speaker_id,
            default_emotion="neutral")
        emotions.update(para_emotions)
        headings.update(para_headings)
        captions.extend(split_keep_spaces(para_removed_tags))

        dialogue = {}
        dialogue["speakerID"] = speaker_id
        dialogue["speak"] = para_removed_tags
        meme["dialogue"][str(i)] = dialogue
    meme["headings"] = headings
    meme["emotions"] = emotions
    meme["captions"] = captions
    meme["state"] = "FORMATTED"
    f = open(str(Path(raw_filename).with_suffix(".json")), "w")
    f.write(json.dumps(meme))
    f.close()
