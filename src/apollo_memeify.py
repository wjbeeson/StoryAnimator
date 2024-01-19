import os.path
import string

from cssutils import CSSParser

from apollo_utils import get_word_list
import apollo_config as config
import logging as log
from pathlib import Path
import json
import re
from PIL import Image
from bs4 import BeautifulSoup


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
        html_file = open(str(Path(raw_filename).with_suffix(".html")), 'r', encoding='utf-8')
        paragraphs = list(BeautifulSoup(html_file.read(), 'lxml').body.findAll('p'))

    # create caption content for each paragraph
    word_count = 0
    captions = []
    headings = {}
    voice_config = json.load(open(str(config.APOLLO_PATH / "config/voice_config.json")))
    styleparser = Styleparser()
    for i, para in enumerate(paragraphs):
        # Step 1: Get the speaker ID and header
        if "title" in para.attrs:
            headings[str(word_count)] = para.attrs["title"]
        emotion = para.attrs["emotion"]
        editing_id = para.attrs["class"][0]
        speaker_id = default_speaker_id
        if editing_id in voice_config:
            speaker_id = voice_config[editing_id]

        # Step 2: Convert the html to text and parse
        raw_text = para.text
        raw_text = raw_text.replace("\n", "")
        raw_text = re.sub(' +', ' ', raw_text)
        text = raw_text + " "

        captions.extend(get_word_list(text, tokens=False))
        word_count += (len(captions) - word_count)

        dialogue = {}
        dialogue["emotion"] = emotion
        dialogue["speakerID"] = speaker_id
        dialogue["styleID"] = styleparser.get_style_id(speaker_id)
        dialogue["speak"] = text
        meme["dialogue"][str(i)] = dialogue

    meme["headings"] = headings
    meme["captions"] = captions
    meme["state"] = "FORMATTED"

    styles = []
    for i in range(len(meme["dialogue"])):
        dialogue = meme["dialogue"][str(i)]
        style_id = dialogue["styleID"]
        word_count = len(get_word_list(dialogue["speak"], tokens=False))
        for j in range(word_count):
            styles.append(style_id)
    meme["styleIDs"] = styles
    f = open(str(Path(raw_filename).with_suffix(".json")), "w")
    f.write(json.dumps(meme))
    f.close()

    # create empty PNG for easy renaming later
    if not os.path.isfile(str(Path(raw_filename).with_suffix(".png"))):
        im = Image.new(mode="RGB", size=(200, 200))
        im.save(str(Path(raw_filename).with_suffix(".png")))

    # create empty COMMENTS file for easy adding
    raw_filepath = Path(raw_filename)
    comments_filepath = raw_filepath.with_suffix(".cmmts")
    with open(comments_filepath, "w") as f:
        f.write("")


#memeify(r"C:\Users\wjbee\Desktop\Raptor\scripts\01.07.2024\New_Daughter_15\New_Daughter_15.txt")
