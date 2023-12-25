import string

from cssutils import CSSParser

from apollo_utils import split_keep_spaces
import apollo_config as config
import logging as log
from pathlib import Path
import json
import re


def get_tag_type(tag):
    tag = tag.replace("<", "").replace(">", "")
    tag_split = tag.split("=")
    tag_type = tag_split[0].translate(str.maketrans('', '', string.punctuation)).strip()
    raw_tag_value = tag_split[1].strip()
    return (tag_type, raw_tag_value)


variable_map = {}


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
            (tag_type, raw_tag_value) = get_tag_type(tag)
            match tag_type:
                case "s" | "speaker":
                    speaker = raw_tag_value.translate(str.maketrans('', '', string.punctuation)).replace(" ",
                                                                                                         "").lower()
                    if speaker in variable_map:
                        speaker = variable_map[speaker]
                case "def" | "speaker_def":
                    split = raw_tag_value.replace(" ", "").split(",")
                    for vm in split:
                        map_split = vm.split(":")
                        variable_map[map_split[0].lower()] = map_split[1].translate(
                            str.maketrans('', '', string.punctuation)).title()
                case "e" | "emotion":
                    char_pos_emotions[start] = raw_tag_value.translate(
                        str.maketrans('', '', string.punctuation)).replace(" ", "").lower()
                case "h" | "heading":
                    char_pos_headings[start] = raw_tag_value
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


class Styleparser():
    def __init__(self, css_filepath=r"C:\Users\wjbee\JSProjects\Remotion\src\styles.css"):

        ids = []
        parser_css = CSSParser(loglevel=log.CRITICAL)
        css_rules = parser_css.parseFile(css_filepath, ).cssRules
        for rule in css_rules:
            ids.append(rule.selectorText.replace("#", ""))

        self.custom_ids = {}
        self.generic_ids = []
        self.generic_ids_copy = []
        for id in ids:
            if id.find("speaker") != -1:
                self.generic_ids.append(id.lower())
            else:
                self.custom_ids[id.lower()] = id.lower()
        self.generic_ids_copy = self.generic_ids.copy()

    def get_style_id(self, speaker_id):
        speaker_id = speaker_id.lower()
        if speaker_id in self.custom_ids:
            return self.custom_ids[speaker_id]
        else:
            if len(self.generic_ids_copy) == 0:
                self.generic_ids_copy = self.generic_ids.copy()
            new_id = self.generic_ids_copy.pop(0)
            self.custom_ids[speaker_id] = new_id
            return new_id


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
    styleparser = Styleparser()
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
        dialogue["styleID"] = styleparser.get_style_id(speaker_id)
        dialogue["speak"] = para_removed_tags
        meme["dialogue"][str(i)] = dialogue
    meme["headings"] = headings
    meme["emotions"] = emotions
    meme["captions"] = captions
    meme["state"] = "FORMATTED"

    styles = []
    for i in range(len(meme["dialogue"])):
        dialogue = meme["dialogue"][str(i)]
        style_id = dialogue["styleID"]
        word_count = len(split_keep_spaces(dialogue["speak"]))
        for j in range(word_count):
            styles.append(style_id)
    meme["styleIDs"] = styles
    f = open(str(Path(raw_filename).with_suffix(".json")), "w")
    f.write(json.dumps(meme))
    f.close()


#memeify(r"C:\Users\wjbee\Desktop\Raptor\scripts\test\test.txt")
