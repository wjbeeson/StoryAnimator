import string
from dataclasses import dataclass
from moviepy.editor import *
from enum import Enum
import re
from matplotlib.transforms import Bbox

from forge.clipanimator.clipanimator import ClipAnimator, TransitionEffectType

from forge.gizehtext import GzTextClip

FONT_SIZE_GUESS = 20
TAB_VALUE = 8

WHITESPACE_CHARS = "\n\t "


def get_tokens(text, discard_ws=True):
    """
    Parses text into a list of word tokens and whitespace tokens
    Returns
    -------

    """
    punctuation = '?.,"!\-:;\'\(\)\/'
    regex = f"[-+*•\w{punctuation}]+|[{WHITESPACE_CHARS}]+"
    return [word for word in re.findall(regex, text) if not discard_ws or word[0] not in WHITESPACE_CHARS]


def count_word_tokens(token_list):
    return len([token for token in token_list if token[0] not in WHITESPACE_CHARS])


def str_remove_any(s, chars_to_remove):
    return s.translate({ord(i): None for i in chars_to_remove})


def strip_ws(text):
    return " ".join(get_tokens(text))


@dataclass
class Font:
    def __init__(self, name, size, color, stroke_color=None, stroke_width=None, highlight_color=None):
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
            stroke_width=self.stroke_width
        )


class TextAlignment(Enum):
    Left = 0,
    Center = 1,
    Right = 2


class Typesetter:

    # leading appeared to be about 10% too large
    @property
    def row_height(self):
        return int(self._fn_calc_word_size("Wy")[1]) * .8  # the np array created by GzTextClip is a bit too tall,
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

        words = get_tokens(text, False)

        # process isolated punctuation
        words_cleaned = []
        trans = str.maketrans("", "", string.punctuation)

        for i, word in enumerate(words):
            if word.translate(trans) == '':
                if i == 0:  # prepend to following word
                    if len(words) > 1:
                        words[i + 2] = word + words[i + 2]
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

        word_count = count_word_tokens(words)

        if word_count > len(sync_values):
            breakpoint()
        assert word_count <= len(sync_values), f"Insufficient sync values for remaining words"

        #
        # attempt to position next word in list
        #

        word = words[0]

        # process whitespace
        if word[0] in WHITESPACE_CHARS:
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
            assert word[0] not in WHITESPACE_CHARS

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
            _, _, _, prev_duration = arrangement[0]

        total_duration = duration + prev_duration

        arrangement_entry = (
            word,
            (int(self._calc_row_alignment(bbox, x, row_lengths[row], alignment)), int(self._y(bbox, row))),
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


Typesetter.PROFANITY_LIST = ["shucks"]
Typesetter.PROFANITY_GRAWLIX = "%@$&*!"
Typesetter.ANONYMOUS = "*****"


def _filter_profanity(words):
    # if not Typesetter.PROFANITY_LIST:
    #   with open(config.FORGE_PROFANITY_LIST, 'r') as f:
    #       Typesetter.PROFANITY_LIST = [ line.strip().lower() for line in f.readlines()]

    def sanitize_word(word):
        if word.lower() in Typesetter.PROFANITY_LIST:
            word = Typesetter.PROFANITY_GRAWLIX
        elif word == "NOSHOW":
            word = Typesetter.ANONYMOUS

        return Typesetter.PROFANITY_GRAWLIX if str_remove_any(word.lower(),
                                                              string.punctuation) in Typesetter.PROFANITY_LIST else word

    return [sanitize_word(word) for word in words]


#    for word in Typesetter.PROFANITY_LIST:
#        result = re.sub('(?i)' + re.escape(word), lambda m: Typesetter.PROFANITY_GRAWLIX, text)
#        text = str(result)

#    return text

class TextClipCache:

    def __init__(self, font: Font):
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
                stroke_color=self._font.stroke_color,
                stroke_width=self._font.stroke_width)

        return self._word_to_clip[item]


class CaptionTypesetter(Typesetter):
    def __init__(self, animator, font, transitions=[TransitionEffectType.NONE, TransitionEffectType.NONE]):

        self._animator = animator
        self._transition_in = transitions[0]
        self._transition_out = transitions[1]

        self._cache = TextClipCache(font)

        # need a copy of the font to create highlight words
        self._font = font

    def show_captions(self,
                      caption_area: Bbox,
                      script,
                      sync_values,
                      total_duration,
                      alignment=TextAlignment.Center,
                      ):
        self._animator: ClipAnimator

        arrangement = self._calc_text_arrangement(
            text=script,
            sync_values=sync_values,  # list of tuples. Timestamps & durations
            bbox=caption_area,
            alignment=alignment,
            fn_calc_word_size=lambda word: self._cache[word].size,
            preserve_whitespace=False,
            force_fit=False)  # since i'm testing various font sizes that won't fit, allow the call to fail

        # use the arrangement to position the clips in space and time.  note it is not necessary
        # to create TextClips here since they are already in the cache.

        parent_clip = ColorClip((1,1)).set_position((0, 0)).set_start(0).set_duration(total_duration).set_opacity(0.0)
        parent_clip = self._animator.add_clip(parent_clip, None)
        positions = []
        for i, (word, position, start_time, duration) in enumerate(arrangement):

            if i < len(arrangement) - 1:
                _, _, next_start_time, _ = arrangement[i + 1]
                word_duration = next_start_time - start_time
            else:
                word_duration = duration
                #duration = duration + 1

            #
            #
            #

            highlight_word = GzTextClip(
                txt=word,
                color=self._font.highlight_color,
                fontsize=self._font.size,
                font=self._font.name,
                stroke_color=self._font.stroke_color,
                stroke_width=self._font.stroke_width)

            # The normal word
            self._animator.add_child_clip(
                parent=parent_clip,
                clip=self._cache[word]
                .set_start(0)
                .set_duration(total_duration),
                relative_pos=position
            )
            positions.append(position)

            # The highlight word
            self._animator.add_child_clip(
                parent=parent_clip,
                clip=highlight_word
                .set_start(start_time)
                .set_duration(word_duration),
                relative_pos=position
            )
            positions.append(position)

        return positions
