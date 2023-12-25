import string
from pathlib import Path
from time import strftime
from time import gmtime
import json
import logging as log

characters_per_line = 20
def add_description(meme_filename):
    class Description:
        def __init__(self, meme_path, first_chapter_name):
            self.meme_path = meme_path
            self.heading_dict = {0: first_chapter_name}

        def add_word(self, word, timestamp):
            self.heading_dict[round(timestamp, 0)] = word

        def write(self):
            with open(self.meme_path.with_suffix(".descr"), "w") as f:
                for i in range(len(self.heading_dict)):
                    time = strftime("%M:%S", gmtime(list(self.heading_dict.keys())[i]))
                    f.write(f"{time} {list(self.heading_dict.values())[i]}\n")

    meme_path = Path(meme_filename)
    meme = json.load(open(str(meme_filename)))
    timestamps = meme["timestamps"]
    description_obj = Description(meme_path, "The Story")
    for header in meme["headings"]:
        description_obj.add_word(meme["headings"][header], timestamps[int(header)])
    description_obj.write()
    log.info("Writing description file")


def calculate_blocks(meme_filename):
    log.info("Calculating text blocks")
    meme = json.load(open(str(meme_filename)))
    captions = meme["captions"]

    block_starts_list = []
    block_ends_list = []

    # calculate blocks
    character_count = 0
    starting_span = 0
    for i, token in enumerate(captions):
        token: string
        word_length = len(token)
        if word_length > characters_per_line:
            raise Exception(f"Word {token} exceeds line length requirement of {characters_per_line} characters")
        if character_count + word_length < characters_per_line and token.find(". ") == -1:
            character_count += word_length
        else:
            character_count = 0
            block_starts_list.append(starting_span)
            block_ends_list.append(i)
            starting_span = i + 1
        if i == len(captions) - 1:
            block_starts_list.append(starting_span)
            block_ends_list.append(i)
    meme["blockStarts"] = block_starts_list
    meme["blockEnds"] = block_ends_list
    return meme


