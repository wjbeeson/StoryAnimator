import string
from dataclasses import dataclass
from moviepy.editor import *
from enum import Enum
import re
from matplotlib.transforms import Bbox

import apollo_utils
import apollo_config as config
from vulcan.clipanimator import ClipAnimator, TransitionEffectType

from vulcan.gizehtext import GzTextClip

FONT_SIZE_GUESS = 20
TAB_VALUE = 8

@dataclass
class Font:
    def __init__(self, name, size, color,  stroke_color=None, stroke_width = None, highlight_color = None):
        self.name = name
        self.size = size
        self.color = color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.highlight_color = highlight_color

    def create_text_clip(self, text):
        return GzTextClip(
            txt=text,
            font=self.name,
            fontsize=self.size,
            color=self.color,
            stroke_color=self.stroke_color,
            stroke_width = self.stroke_width
        )


class TextAlignment(Enum):
    Left = 0,
    Center = 1,
    Right = 2


class Typesetter:

    # leading appeared to be about 10% too large
    @property
    def row_height(self):
        return int(self._fn_calc_word_size("Wy")[1]) * .8 # the np array created by GzTextClip is a bit too tall,
                                                          # easier to correct for it here

    @property
    def word_spacing(self):
        return int(self._fn_calc_word_size("e")[0])

    def _y(self, bbox, row):
        return int(bbox.ymin + row * self.row_height)


    def _calc_text_arrangement(self,
                               text: str,
                               sync_values: list[float, float],
                               bbox: Bbox,
                               alignment: TextAlignment,
                               fn_calc_word_size,
                               force_fit,
                               preserve_whitespace: bool = True,
                               one_pass: bool = False
                               ):
        """Calculates the start time, duration and position for each word in a text string

        Parameters
        ----------
        text - the text to be arranged
        sync_values - a list of start_time,duration tuples for each word
        bbox - a bounding box representing the dimensions of the text display area
        alignment - left, right or center
        fn_calc_word_size - a callback function returns the size of a word
        one_pass - True if the text must all fit in the specified area, False if multiple arrangements
        are allowed

        Returns
        -------
        list[(x,y),start_time,duration]
        """

        # cache on this instance to reduce function call parameter noise
        self._fn_calc_word_size = fn_calc_word_size

        #
        # text can contain formatting codes.  currently it's just \n - linefeed.   and
        # the code can appear more than once. to simplify processing, parse the text
        # into a list of word,code tuples e.g. [('end',None),('of',None),('sentence','\n\n\n')
        #

        words = apollo_utils.get_tokens( text, False)

        # process isolated punctuation
        words_cleaned = []
        trans = str.maketrans("", "", string.punctuation)

        for i,word in enumerate(words):
            if word.translate(trans)=='':
                if i == 0: # prepend to following word
                    if len(words) > 1:
                        words[i+2] = word + words[i+2]
                else:
                    words_cleaned[-2] = words_cleaned[-2] + word

                words.pop(0)
            else:
                words_cleaned.append(word)

#        while words:
#            word = words.pop(0)
#            if word in string.punctuation:
#                words.pop(0)
#            else:
#                words_cleaned.append(word)

        words = words_cleaned
        words = _filter_profanity(words)

        text_arrangement: list(str, (int, int), float, float)  # word, position, start, duration
        text_arrangement = []

        #
        # determine the row spacing necessary to perform vertical justification
        #

        self._rows = 1
        for word in words:
            if '\n' in word: self._rows += word.count('\n')

#        self._justified_height = (bbox.height - self._rows * self.row_height) / (self._rows-1)

        while words:
            row_lengths = [0]
            x, _ = bbox.get_points()[0]

            # arrange as many of the words as possible.  note this may completely fill the caption
            # area in which case additional call(s) will be necessary

            partial_arrangement = self._arrange_words(
                words,
                sync_values,
                bbox,
                row_lengths,
                x,
                0,
                alignment,
                not preserve_whitespace,
                force_fit
            )

            if not partial_arrangement:
                # not possible to place any words, which means the text area is too small for the
                # word/font/font size combination.  this is a fatal error
                raise ValueError(f"Insufficient space in text area for {text}")

            # accumulate the arrangement and consume the words that were placed
            text_arrangement += partial_arrangement

            # if the text didn't all fit and one_pass as specified, no need to continue.  this logic is used
            # for font size determination
            if words and one_pass:
                return None


        return text_arrangement

    def _arrange_words(self,
                       words: list[str],
                       sync_values: list[(float, float)],
                       bbox: Bbox,
                       row_lengths: list[int],
                       x,
                       row,
                       alignment,
                       add_linebreaks,
                       force_fit
                       ):
        """
        Recursive function that returns the arrangement for the specified text.
        Parameters
        ----------
        words
        sync_values
        bbox
        row_lengths
        x
        row
        alignment

        Returns  [(word, (x,y), start_time, duration) ...]
        -------

        """
        if not words: return []

        word_count = apollo_utils.count_word_tokens(words)

        if word_count > len(sync_values):
            breakpoint()
        assert word_count <= len(sync_values), f"Insufficient sync values for remaining words"

        #
        # attempt to position next word in list
        #

        word = words[0]

        # process whitespace
        if word[0] in apollo_utils.WHITESPACE_CHARS:
            for char in word:
                match char:
                    case '\t':
                        x += self.word_spacing * TAB_VALUE
                        row_lengths[row] += self.word_spacing * TAB_VALUE

                    case '\n':
                        row += 1
                        row_lengths.append(0)
                        x, _ = bbox.get_points()[0]  # start at beginning of next row

                    case ' ':
                        x += self.word_spacing
                        row_lengths[row] += self.word_spacing

                    case _:
                        raise NotImplementedError("Unsupported whitespace")

            # get the next word, which should be non-ws
            words.pop(0)

            # the text ended with whitespace.  it's allowed, but doesn't make any sense
            if not words: return []

            word = words[0]
            assert word[0] not in apollo_utils.WHITESPACE_CHARS

        # use the callback to get the word size
        width, height = self._fn_calc_word_size(word)


        if not bbox.contains(x + width, self._y(bbox, row) + height):
            if not force_fit and not add_linebreaks:
                return []
            elif add_linebreaks:
                # current line is too long, try next line
                x, _ = bbox.get_points()[0]
                row += 1
                if not bbox.contains(x + width, self._y(bbox, row) + height):
                    return []  # no more clips can be positioned

            row_lengths.append(0)

        row_lengths[row] += width

        words.pop(0)
        start_time, duration = sync_values.pop(0)

        arrangement = self._arrange_words(
            words,
            sync_values,
            bbox,
            row_lengths,
            x + width,
            row,
            alignment,
            add_linebreaks,
            force_fit)

        # all the words that are arranged together should have the same duration, so they all vanish
        # at the same time. so the duration for the current word is the duration of that word plus
        # the sum of the durations in the arrangement

        prev_duration = 0
        if arrangement:
            _,_,_,prev_duration = arrangement[0]

        total_duration = duration + prev_duration

        arrangement_entry = (
            word,
            (int(self._calc_row_alignment( bbox, x, row_lengths[row], alignment )),int(self._y(bbox, row))),
            start_time,
            total_duration
        )

        return [arrangement_entry] + arrangement


    def _calc_row_alignment(self, bbox, x, row_length, alignment):
        match alignment:
            case TextAlignment.Left:
                dx = 0
            case TextAlignment.Right:
                dx = bbox.width - row_length
            case TextAlignment.Center:
                dx = bbox.width / 2 - row_length / 2
            case _:
                raise ValueError()

        return x + dx

Typesetter.PROFANITY_LIST = None
Typesetter.PROFANITY_GRAWLIX = "%@$&*!"
Typesetter.ANONYMOUS = "*****"

def _filter_profanity(words):
    if not Typesetter.PROFANITY_LIST:
        with open(config.FORGE_PROFANITY_LIST, 'r') as f:
            Typesetter.PROFANITY_LIST = [ line.strip().lower() for line in f.readlines()]

    def sanitize_word(word):
        if word.lower() in Typesetter.PROFANITY_LIST:
            word = Typesetter.PROFANITY_GRAWLIX
        elif word == "NOSHOW":
            word = Typesetter.ANONYMOUS

        return Typesetter.PROFANITY_GRAWLIX if apollo_utils.str_remove_any( word.lower(), string.punctuation) in Typesetter.PROFANITY_LIST else word

    return [sanitize_word(word) for word in words]

#    for word in Typesetter.PROFANITY_LIST:
#        result = re.sub('(?i)' + re.escape(word), lambda m: Typesetter.PROFANITY_GRAWLIX, text)
#        text = str(result)

#    return text

class TextClipCache:

    def __init__(self, font : Font):
        assert font.name
        assert font.size
        assert font.color

        self._font = font
        self._word_to_clip = {}

    def __getitem__(self, item):
        if item not in self._word_to_clip:
            self._word_to_clip[item] = GzTextClip(
                txt=item,
                color=self._font.color,
                fontsize=self._font.size,
                font=self._font.name,
                stroke_color= self._font.stroke_color,
                stroke_width= self._font.stroke_width)

        return self._word_to_clip[item]

class CaptionTypesetter(Typesetter):
    def __init__(self, animator, font, transitions=[TransitionEffectType.NONE,TransitionEffectType.NONE]):

        self._animator = animator
        self._transition_in = transitions[0]
        self._transition_out = transitions[1]

        self._cache = TextClipCache(font)

        # need a copy of the font to create highlight words
        self._font = font

    def show_captions(self, caption_area : Bbox, text, sync_values, alignment=TextAlignment.Center):

        arrangement = self._calc_text_arrangement(
            text=apollo_utils.strip_ws(text),
            sync_values = sync_values,
            bbox = caption_area,
            alignment = alignment,
            fn_calc_word_size= lambda word :  self._cache[word].size,
            preserve_whitespace=False,
            force_fit=False)  # since i'm testing various font sizes that won't fit, allow the call to fail

        # use the arrangement to position the clips in space and time.  note it is not necessary
        # to create TextClips here since they are already in the cache.
        for i,(word,position,start_time,duration) in enumerate(arrangement):

            if i < len(arrangement) - 1:
                _, _, next_start_time, _ = arrangement[i + 1]
                word_duration = next_start_time - start_time
            else:
                word_duration = duration

            #
            #
            #


            highlight_word = GzTextClip(
                    txt=word,
                    color=self._font.highlight_color,
                    fontsize=self._font.size,
                    font=self._font.name,
                    stroke_color=self._font.stroke_color,
                    stroke_width=self._font.stroke_width )

            self._animator.add_clip(highlight_word.set_position( position )
                                   .set_start( start_time )
                                   .set_duration( word_duration ), self._transition_in)

            self._animator.add_clip(self._cache[word].set_position( position )
                                   .set_start( start_time+word_duration )
                                   .set_duration( duration-word_duration),)

class TextBubbleTypesetter(Typesetter):
    def __init__(self, animator, transitions=[TransitionEffectType.NONE,TransitionEffectType.NONE]):
        self._animator = animator
        self._transition_in = transitions[0]
        self._transition_out = transitions[1]


    @staticmethod
    def calc_max_point_size(parent_clip, text, bbox, font_name, guess):
        def perform_test(size):
            animator = ClipAnimator( tuple(map(int, config.FORGE_SCREEN_SIZE.split(","))))
            font = Font(font_name, 0, "black")
            ts = TextBubbleTypesetter(animator, [None, None])
            word_count = apollo_utils.count_words(text)
            timestamps = list(zip(range(word_count), [1] * word_count))

            font.size = size
            cache = TextClipCache(font)

            try:

                return ts._calc_text_arrangement(
                    text=text,
                    sync_values=timestamps,
                    bbox = bbox,
                    alignment=TextAlignment.Left, # don't matter tho
                    fn_calc_word_size=  lambda word : cache[word].size,
                    one_pass=True,# fail if all clips couldn't be placed at once
                    preserve_whitespace=True,
                    force_fit=False)
            except ValueError as x:
                return False




        def guess_answer(guess, compare_fn):

            low = None  # highest good guess
            high = None  # lowest bad guess
            PROBE_RANGE = 4

            while True:
                if compare_fn(guess):
                    if high == guess + 1:
                        return guess

                    low = guess
                    if high is not None:
                        guess += (high - guess) // 2
                    else:
                        guess += PROBE_RANGE
                    if high is not None and guess >= high:
                        guess = high - 1
                else:
                    high = guess
                    if low == guess - 1:
                        return low

                    if low is not None:
                        guess -= (guess - low) // 2
                    else:
                        guess -= PROBE_RANGE

                    if low is not None and guess <= low:
                        guess = low + 1

        return guess_answer(guess, lambda n: perform_test(n))

    def show_bubble_text(self,
                         font: Font,
                         parent_clip,
                         bbox: Bbox,
                         text,
                         alignment,
                         timestamps,
                         calculate_only ):

        global FONT_SIZE_GUESS

        self._font = font
        if not self._font.size:  # calculated if not provided
            self._font.size = TextBubbleTypesetter.calc_max_point_size(parent_clip, text, bbox, self._font.name,
                                                                       FONT_SIZE_GUESS)
            print(f"Selected {self._font.size} for {text}")
            # use the most recently detected size as the next guess
            FONT_SIZE_GUESS = self._font.size+1

        cache = TextClipCache(font)

        arrangement = self._calc_text_arrangement(
            text,
            timestamps,
            bbox,
            alignment,
            lambda word : cache[word].size,
            preserve_whitespace=True,  # ws for text bubbles is significant
            force_fit=True)             # the selected font size may be slightly too large since it could have
                                        # been specified by user, so don't fail if it overruns the text bubble
                                        # area

        if not calculate_only:
            # use the arrangement to position the clips in space and time.  note it is not necessary
            # to create TextClips here since they are already in the cache.

            #
            # vertical justification
            #

            if self._rows != 1:
                vjust = (bbox.height - self._rows * self.row_height) / (self._rows - 1)
                row = 0
                last_y = -1
                for i,(word,position,start_time,duration) in enumerate(arrangement):
                    x,y = position
                    if last_y == -1:
                       last_y = y

                    if y != last_y:
                        row += 1
                        last_y = y

                    position = (x,y+vjust*row)
                    arrangement[i] = (word,position, start_time, duration)

            # highlight word transition

            for i,(word,position,start_time,duration) in enumerate(arrangement):

                highlight_word = GzTextClip(
                    txt=word,
                    color=self._font.highlight_color,
                    fontsize=self._font.size,
                    font=self._font.name,
                    stroke_color=self._font.stroke_color if self._font.stroke_color else self._font.color ,
                    stroke_width=self._font.stroke_width if self._font.stroke_width else 1)

                if i < len(arrangement)-1:
                    _,_,next_start_time,_ = arrangement[i+1]
                    word_duration = next_start_time - start_time
                else:
                    word_duration = duration

                # highlight effect
                self._animator.add_child_clip(
                    parent_clip,
                    # no need to set position - it will be done by the parent clip
                    highlight_word.set_duration(word_duration).set_start(start_time),
                    position,
                    TransitionEffectType.POP)

                # normal effect, after highlight "wears off"
                self._animator.add_child_clip(
                    parent_clip,
                    # no need to set position - it will be done by the parent clip
                    cache[word].set_start(start_time+word_duration),#.set_duration(duration),
                    position,
                    None )






