import pathlib
import string

import pandas as pd
import statistics
import dto
import dto_utils
import numpy as np
import re
# opencv-python
import cv2
import xml.etree.ElementTree as XmlElementTree
import io

from string import punctuation

import random

from apollo_coloranalyser import ColorAnalyser


def select_random_element(l):
    return l[random.randrange(0,len(l))]

def hex_to_rgb(hex):
  return tuple(int(hex.replace('#','')[i:i+2], 16) for i in (0, 2, 4))
def rgb_to_hex(rgb):
    return '0x{0:02x}{1:02x}{2:02x}'.format(*rgb)

def get_narration_filename( meme_filename, panel_index, narration_index ):
    path = pathlib.Path(meme_filename)
    narration_filename = path.parent / (path.stem + f"_{panel_index}_{narration_index}")
    narration_filename = str(narration_filename.with_suffix(".wav"))
    return narration_filename

def bgr_int_to_rgb_hex(value):
  # check if the value is a valid int between 0 and 16777215
  if not isinstance(value, int) or value < 0 or value > 16777215:
    return None
  # use bitwise operations to extract the red, green and blue components
  blue = (value >> 16) & 255
  green = (value >> 8) & 255
  red = value & 255
  # return a tuple of the components
  return rgb_to_hex((red, green, blue))

def rgb_to_tuple(rgb):
  # assuming rgb is an int in the range 0 to 16777215
  # use bitwise operations to extract the red, green and blue channels
  red = (rgb >> 16) & 255
  green = (rgb >> 8) & 255
  blue = rgb & 255
  # return a tuple of the channels
  return (red, green, blue)

def pick_foreground( background_rgb : (int,int,int)):
    red,green,blue = background_rgb
    if (red * 0.299 + green * 0.587 + blue * 0.114) > 186:
        return "0x000000"
    else:
        return "0xffffff"

def detect_text_colors( rgb, bbox = None ):
    if bbox is not None:
        rgb = bbox.slice(rgb)

    df = pd.DataFrame( np.dstack((rgb, np.zeros(rgb.shape[:2], 'uint8'))).view('uint32').squeeze(-1).flatten())
    value_counts = df[0].value_counts()
    background = parse_color(bgr_int_to_rgb_hex(int(value_counts.keys()[0])))
    font = parse_color(pick_foreground( rgb_to_tuple( int(background.replace("#",""),16) )))

#    sanity check - no longer necessary
#    ca = ColorAnalyser( rgb )
#    background2, font2 = ca.get_hex()
#    font2 = "#"+font2
 #   assert background == background2, f"background color detection algorithms returned different results: {background} , {background2} "
 #   assert font == font2, f"text color detection algorithms returned different results: {font}, {font2}"


    return background, font
def parse_color(s):
    s = s.replace('0x','')
    return f"#{'0' * (6-len(s))}{s}"
def detect_best_text_colors( raw_data, panels : list[dto.PanelType], speaker_num):
    def best_color( colors ):
        if not colors:
            return None

        # https://github.com/fjb595/Apollo/issues/47 pad to 6 characters to prevent textmagick exceptions
        s = hex(statistics.mode([int(h, 16) for h in colors])).replace('0x', "")

    bl = []
    fl = []
    for panel in panels:
        if panel.text_bubble is not None and panel.speaker == speaker_num:

# thanks for nothing, chatgpt
#            b,f = detect_text_colors_kmeans(raw_data,dto_utils.bndbox_to_bbox( panel.text_bubble ))

            return detect_text_colors(raw_data, dto_utils.bndbox_to_bbox( panel.text_bubble ))


    # no text bubble panels for the specified speaker.  it could be the editor assigned a speaker number
    # to a picture panel, or a panel with only a caption.  either case is non-fatal
    return None, None

def get_natural_orientation( size : (int,int)):
    w,h = size
    if .8333 < w/h < 1.2:
        orientation = None # square-ish
    elif w > h:
        orientation = dto.OrientationType.LANDSCAPE
    else:
        orientation = dto.OrientationType.PORTRAIT

    return orientation


def str_remove_any(s, chars_to_remove):
    return s.translate({ord(i): None for i in chars_to_remove})



WHITESPACE_CHARS = "\n\t "

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




#tokens = get_tokens("this is a test")
#tokens = get_tokens("this is   a\n\ttest")
#tokens = get_tokens("this is   a\n\ttest",False)
#tokens = get_tokens("this is   a\n\ttest",True)
#count = count_word_tokens( get_tokens("this is   a\n\ttest",False))


def update_meme_state(meme_filename, state: dto.StateType):
    with open(meme_filename, 'r') as f:
        tree = XmlElementTree.parse(f)

    root = tree.getroot()
    root.find("Header/State").text = state.value
    tree.write(meme_filename)


pass