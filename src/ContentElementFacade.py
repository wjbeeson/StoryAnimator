import io
import re
import xml.etree.ElementTree as XmlElementTree
from xsdata.formats.dataclass.serializers.config import SerializerConfig
from xsdata.formats.dataclass.serializers import XmlSerializer

import dto
import dto_utils



#
# provides a consistent interface to the various content element types defined in the meme DTO.
#
class ContentElementFacade:


    def __str__(self):
        if self.type == dto.ContentType.PICTURE:
            return f"ContentElementFacade(type=Picture, duration = {self.duration})"
        else:
            return f"ContentElementFacade(type={self.type}, text = {self.text[:10]}..."



    # helper function for returning the value of the optional speak element.
    # special processing is required because this element can contain any ssml element, which are
    # not recognized by the meme schema.  so i have to use xpath to obtain the raw value as a string
    def _get_speak_text(self,panel_num, content_num):
        fobj = io.StringIO(self._meme_text)
        tree = XmlElementTree.parse(fobj)
        root = tree.getroot()
        text_node = root.find(f'Panels[{panel_num}]/Content[{content_num}]/*[1]/speak')
        if text_node is not None:
            result =  XmlElementTree.tostring(text_node, encoding='unicode', method='xml')
        else:
            result = ""

        return result

    def initialize(self, ocr, clean, dont_animate,zoom, text, speak, font,  duration,  timestamps=None ):
        self._ocr = ocr
        self._clean = clean
        self._dont_animate = dont_animate
        self._zoom = zoom
        self._text = text
        self._speak = speak
        self._font = font
        self._duration = duration
        self._timestamps = timestamps


    # the panel and content indicies are required to parse the speak element
    def __init__(self, meme : dto.Meme,  panel_index, content_index ):
        content = meme.panels[panel_index].content[content_index]
        assert content.type
        self.type = content.type

        # these values will be used in an xpath selector, and are 1-based
        self._panel_num = panel_index+1
        self._content_num = content_index+1

        # save the serialized meme to a static for later use in speak element processing
        f = io.StringIO()
        XmlSerializer(SerializerConfig(xml_declaration=False, pretty_print=False)).write(f, meme)
        self._meme_text = f.getvalue()

        self._content_element = None
        t = None
        match self.type:
            case dto.ContentType.TEXT_BUBBLE:
                self._content_element = content.text_bubble
                t = self._content_element
                self.initialize(
                    ocr=t.ocr,
                    clean=t.clean,
                    dont_animate=None,
                    zoom = None,
                    text=t.text,
                    speak=self._get_speak_text(
                        panel_num=self._panel_num,
                        content_num=self._content_num),
                    font=t.font, duration=t.duration,
                    timestamps=t.timestamps)

            case dto.ContentType.PICTURE:

                self._content_element = content.picture
                t = self._content_element
                self.initialize( ocr = False, clean=t.clean, dont_animate= t.dont_animate, zoom = t.zoom, text = None, speak = "",
                                 font = None,
                                  duration=t.duration)

            case dto.ContentType.CAPTION:
                self._content_element= content.caption
                t = self._content_element
                self.initialize(
                    ocr = t.ocr,
                    clean = False,
                    dont_animate=None,
                    zoom = None,
                    text = t.text,
                    speak= self._get_speak_text(
                        panel_num=self._panel_num,
                        content_num=self._content_num),
                    font = None,
                    duration=t.duration,
                    timestamps=t.timestamps)




    @property
    def xmin(self):
        return self._content_element.xmin

    @xmin.setter
    def xmin(self,value):
        self._content_element.xmin = value

    @property
    def xmax(self):
        return self._content_element.xmax

    @xmax.setter
    def xmax(self, value):
        self._content_element.xmax = value

    @property
    def ymin(self):
        return self._content_element.ymin


    @ymin.setter
    def ymin(self, value):
        self._content_element.ymin = value


    @property
    def ymax(self):
        return self._content_element.ymax


    @ymax.setter
    def ymax(self, value):
        self._content_element.ymax = value

    # return text with reactions removed
    @property
    def text(self):

        # just return empty string for non-text elements like picture.  simplifies processing
        # for the caller
        if not hasattr(self._content_element,'text'):
            return ""

        # when a meme is deserialized, the text element has an object structure because it can contain
        # <R> elements.  but if the text setter has been called, it will contain a string.  So i need
        # to handle both cases
        elif isinstance(self._content_element.text,str):
            # text setter has bee called, return the string
            return self._content_element.text
        elif self._content_element.text and self._content_element.text.content:
            # text contains a combination of text and R elements
            _text, reactions =  dto_utils.get_panel_text(self._content_element.text.content)
            return _text
        else:
            return ""

        return self._content_element.text


    # changing the text property of the wrapper should change the underlying content element, unless
    # it's a picture, which doesn't support text
    @text.setter
    def text(self,value):
        assert self.type != dto.ContentType.PICTURE
        self._content_element.text = value

    # returns text, reaction list
    @property
    def reaction_text(self):
        if self._content_element.text and self._content_element.text.content:
            return  dto_utils.get_panel_text(self._content_element.text.content)
        else:
            return "",[]


    @property
    def timestamps(self):
        return self._content_element.timestamps

    @timestamps.setter
    def timestamps(self,value):
        self._content_element.timestamps = value

    @property
    def ocr(self):
        return self._ocr

    @property
    def clean(self):
        return self._clean

    @property
    def dont_animate(self):
        return self._dont_animate

    @property
    def zoom(self):
        return self._zoom

    @property
    def speak(self):
        return self._speak

    @speak.setter
    def speak(self,value):
        self._content_element.speak = value


    #
    # convenience function to simplify use of the text/speak elements
    #
    # returns the string value of the speak element, if present, otherwise the processed string
    # value of the text element, sans reactions
    #
    @property
    def speech_text(self):
        t = self.speak if self._speak else self.text
        return t if t is not None else ""


    @property
    def font(self):
        return self._font

    @property
    def background(self):
        return self._content_element.background

    @background.setter
    def background(self,value):
        self._content_element.background =value

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self,value):
        self._content_element.duration = value

    @property
    def group(self):
        return self._content_element.group

    @group.setter
    def group(self,value):
        self._content_element.group =value



ContentElementFacade.resize = dto_utils.resize_bndbox

#
# group adjacent text bubbles for same speaker.  this is necessary for the common case where
# a single line of narration is split between two or more text bubbles, and thus must be spoken
# all at once
#
def create_content_element_groups( meme : dto.Meme ):
    # list[ (panel_index, line_num,list[content_index]) ]  line_num refers to a line of spoken narration within a panel
    groups = []
    for i, panel in enumerate(meme.panels):
        line_num=0
        for l, content in enumerate(panel.content):
            ce = ContentElementFacade(meme=meme, panel_index=i, content_index=l)

            if ce.type in [dto.ContentType.TEXT_BUBBLE] and groups:
                i_prev, prev_line_num, group_prev = groups[-1]
                l_prev = group_prev[-1]
                content_prev = meme.panels[i_prev].content[l_prev]
                if i == i_prev and content_prev.speaker == content.speaker \
                        and content_prev.type == dto.ContentType.TEXT_BUBBLE:
                    group_prev.append(l)
                    groups[-1] = (i_prev,prev_line_num, group_prev)
                    continue

            groups.append((i,line_num, [l]))
            line_num += 1

    return groups




def _normalize_text(text):


    ssml = False

    if text.startswith("<speak>") and text.endswith("</speak>"):
        ssml = True
        text = text.replace("<speak>","").replace("</speak>","")

    return ssml, text


def _combine_text(t1, t2):
    ssml1, t1 = _normalize_text(t1)
    ssml2, t2 = _normalize_text(t2)
    text = " ".join([t1, t2])

    if ssml1 or ssml2:
        text = f"<speak>{text}</speak>"

    return text


def combine_text_elements(meme, panel_num, content_nums: list[dto.ContentType]):
    text = None

    for content_num in content_nums:
        ce = ContentElementFacade(meme, panel_num, content_num)
        if text:
            text = _combine_text(text, ce.speech_text)
        else:
            text = ce.speech_text

    return text
