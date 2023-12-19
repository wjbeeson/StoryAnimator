import shutil
import string
import uuid

import dto
import dto_utils
from pathlib import Path
import numpy as np
from moviepy.editor import *
from apollo_utils import get_narration_filename, get_tokens
from apollo_timestamp import normalize_tokens
from time import strftime
from time import gmtime

class Description:
    def __init__(self, meme_path, first_chapter_name):
        self.meme_path = meme_path
        self.word_tokens = [first_chapter_name]
        self.word_timestamps = [0]

    def add_word(self, word, timestamp):
        self.word_tokens.append(word)
        self.word_timestamps.append(timestamp)
    def write(self):
        with open(self.meme_path.with_suffix(".descr"), "w") as f:
            for i in range(len(self.word_tokens)):

                time = strftime("%M:%S", gmtime(self.word_timestamps[i]))
                f.write(f"{time} {self.word_tokens[i]}\n")
#
# transform a timestamped meme + narrations to the input file format expected by William's
# javascript forge
#
def transform_meme(meme_filename):
    meme_path = Path(meme_filename)
    meme = dto.Meme.read(meme_filename)
    duration = 0.0
    timestamps = []
    tokens = []
    clips = []
    for i, content in enumerate(meme.panels[0].content):
        caption_content = content.caption

        timestamps.extend(np.round(
            (np.array(caption_content.timestamps) + duration), 2).tolist())
        text_content = caption_content.text.content[0]
        t = get_tokens(text_content)

        # append punctuation islands to preceding token e.g.
        #    This is a - Test
        # becomes
        #    This
        #    is
        #    a -
        #    Test

        temp = []
        for l, token in enumerate(t):
            # check for puncutation island
            if not normalize_tokens([token]):
                if len(temp):
                    temp[-1] = temp[-1] + " " + token
                else:
                    # island is first token, so attach to the next
                    t[l + 1] = token + " " + t[l + 1]
            else:
                temp.append(token)

        t = temp

        for l in range(len(t) - 1):
            t[l] = t[l] + " "

        #timestamps.append(timestamps[len(timestamps) - 1])
        #t.append("<br>")
        # t[len(t)-1] = t[len(t)-1] + "<br>"
        tokens.extend(t)

        assert len(timestamps) == len(tokens)

        narration_filename = get_narration_filename(meme_filename, 0, i)

        clip = AudioFileClip(narration_filename)
        duration += clip.duration
        clips.append(clip)
    chapter_start = 0
    searching_for_end = False
    chapter_words = []
    description_obj = Description(meme_path, "The Story")
    for i, token in enumerate(tokens):
        if token.find("^") != -1 and token.find("^") != token.rfind("^"):
            searching_for_end = False
            chapter_words.append(token)
            description_obj.add_word(" ".join(chapter_words).replace("^", ""), chapter_start)
            chapter_words = []
        elif token.find("^") != -1:
            if searching_for_end:
                searching_for_end = False
                chapter_words.append(token)
                description_obj.add_word(" ".join(chapter_words).replace("^",""), chapter_start)
                chapter_words = []
            else:
                chapter_start = timestamps[i]
                searching_for_end = True
        if searching_for_end:
            chapter_words.append(token)
    description_obj.write()
    #
    # create forge input file in expected format
    #
    parameters = []
    word_timestamps = ""
    characters_per_line = 20
    variable_header = "export const"
    word_tokens = f"{variable_header} _words = "
    word_timestamps = f"{variable_header} _timestamps = "
    block_starts = f"{variable_header} _blockStarts = "
    block_ends = f"{variable_header} _blockEnds = "

    word_tokens_list = []
    word_timestamps_list = []
    block_starts_list = []
    block_ends_list = []

    parameters = []
    with open(meme_path.with_suffix(".ts"), "w") as f:
        # words
        for i in range(len(tokens)):
            word_tokens_list.append(tokens[i])
        word_tokens += (word_tokens_list.__str__())
        # timestamps
        for i in range(len(timestamps)):
            word_timestamps_list.append(timestamps[i])
        word_timestamps += (word_timestamps_list.__str__())
        # calculate blocks
        character_count = 0
        starting_span = 0
        for i, token in enumerate(tokens):
            token: string
            word_length = len(token)
            if word_length > characters_per_line:
                raise Exception(f"Word {token} exceeds line length requirement of {characters_per_line} characters")
            if character_count + word_length < characters_per_line and token.find(". ") == -1:
                character_count += word_length
            else:
                print(character_count)
                print(token)
                character_count = 0
                block_starts_list.append(starting_span)
                block_ends_list.append(i)
                starting_span = i + 1
            if i == len(tokens) - 1:
                block_starts_list.append(starting_span)
                block_ends_list.append(i)

        block_starts += (block_starts_list.__str__())
        block_ends += (block_ends_list.__str__())

        parameters = [word_tokens, word_timestamps, block_starts, block_ends]
        for prop in parameters:
            f.write(f"{prop}\n\n\n")
    final = concatenate_audioclips(clips)
    final.write_audiofile(str((meme_path.parent / meme_path.stem).with_suffix(".wav")))
