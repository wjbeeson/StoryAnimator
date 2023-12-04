from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.serializers import XmlSerializer

from xsdata.formats.dataclass.context import XmlContext
from xsdata.formats.dataclass.parsers import XmlParser

from xml.sax.saxutils import unescape
import numpy as np

import xmlschema
from pathlib import Path

from moviepy.editor import *

from matplotlib.transforms import Bbox

import apollo_utils
# pip install xsdata[cli]
# venv\scripts\xsdata meme.xsd --package dto
import dto


import apollo_config as config




def meme_write(self, filename,force=False ):
    mode = "w" if force else "x"
    with open(file=filename, mode=mode,encoding='utf-8') as f:
        XmlSerializer( SerializerConfig( xml_declaration=False, pretty_print= False)).write(f,self)

    xsd = xmlschema.XMLSchema(config.MEME_XSD_FILENAME)

    assert xsd.is_valid(filename)


def deserialize( f, t):
    return XmlParser(context=XmlContext()).parse(f, t)

def dto_read(filename, type=dto.Meme):
    xsd = xmlschema.XMLSchema(config.MEME_XSD_FILENAME)
    assert xsd.is_valid(filename)

    with open( filename, "r", encoding="utf-8") as f:
        return XmlParser(context=XmlContext()).parse(f,type)


def create_narration_clips( meme_path, count ):
    meme_path = Path(meme_path)
    for i in range(count):
        yield AudioFileClip(f"{meme_path.parent/meme_path.stem}_{i}.wav")

# returns text, [(word count, <rxn>)]
def get_panel_text(message_content):
    text = ""

    # list of zero-based indices of words marked with SFX tags (tag preceeds word)
    l = []

    word_count = 0
    for fragment in message_content:
        if type(fragment) is str:
            fragment = unescape(fragment)
            word_count += apollo_utils.count_words(fragment)
            text += fragment
        else:
            l.append((word_count,fragment))

    return text, l


def resize_bbox( self : Bbox, scale : float ):
    return Bbox(np.reshape(self.get_points().flatten() * float,(2,2)))


def resize_bndbox( self : dto.BoundingBoxType, scale : float ):
    self.xmin = int( self.xmin * scale)
    self.xmax = int( self.xmax * scale)
    self.ymin = int( self.ymin * scale)
    self.ymax = int( self.ymax * scale)

    return self


def bbox_to_bndbox(bbox : Bbox):
    """
Create VOC/.meme bndbox from matplotlib Bbox
    :param bbox: matplotlib Bbox
    :return: VOC/.meme bndbox
    """


    return dto.BoundingBoxType(*bbox.get_points().flatten().astype('int'))

def bbox_to_text_bubble(bbox : Bbox):
    """
Create VOC/.meme bndbox from matplotlib Bbox
    :param bbox: matplotlib Bbox
    :return: VOC/.meme bndbox
    """


    return dto.TextBubbleType(*bbox.get_points().flatten().astype('int'))

def bndbox_to_bbox( bndbox ):
    """
Create matplotlib Bbox from VOC/.meme bndbox
    :param bndbox: VOC.meme bndbox
    :return: matplotlib Bbox
    """
    return Bbox([[bndbox.xmin, bndbox.ymin],[bndbox.xmax, bndbox.ymax]])


# patch some Dto classes.  I do this here b/c they are machine generated so I can't change the Source

dto.Meme.read = dto_read
dto.Meme.write = meme_write

def slice_img_data(self : Bbox, img_data ):
    x1,y1,x2,y2 = self.get_points().astype('int').flatten()

    return img_data[y1:y2,x1:x2,:]

Bbox.slice = slice_img_data
Bbox.resize = resize_bbox


dto.BoundingBoxType.resize = resize_bndbox

