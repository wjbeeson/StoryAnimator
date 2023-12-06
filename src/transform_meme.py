import string

import dto
import dto_utils
from pathlib import Path
import numpy as np
from moviepy.editor import *
from apollo_utils import get_narration_filename, get_tokens
from apollo_timestamp import normalize_tokens


#
# transform a timestamped meme + narrations to the input file format expected by William's
# javascript forge
#
def transform_meme( meme_filename ):
    meme_path = Path(meme_filename)
    meme = dto.Meme.read(meme_filename)

    duration = 0.0
    timestamps = []
    tokens = []
    clips = []
    for i,content in enumerate(meme.panels[0].content):
        caption_content = content.caption
        timestamps.extend( np.round(
            (np.array(caption_content.timestamps) + duration),2).tolist())
        t = get_tokens(caption_content.text.content[0])

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
                    t[l+1] = token + " " + t[l+1]
            else:
                temp.append(token)

        t = temp

        for l in range(len(t)-1):
            t[l] = t[l]+" "

        t[len(t)-1] = t[len(t)-1] + "<br><br>"
        tokens.extend( t)

        assert len(timestamps) == len(tokens)

        narration_filename = get_narration_filename(meme_filename,0,i)

        clip = AudioFileClip(narration_filename)
        duration += clip.duration
        clips.append(clip)

    #
    # create forge input file in expected format
    #

    with open(meme_path.with_suffix(".forge"),"w") as f:
        for i in range(len(timestamps)):
            f.write(f"{tokens[i]}||{timestamps[i]}\n")

    final = concatenate_audioclips(clips)
    final.write_audiofile(str((meme_path.parent / meme_path.stem).with_suffix(".wav")))


#transform_meme(r"C:\Users\fjbee\PycharmProjects\Raptor\test\lifes_work.meme")