import statistics
import numpy as np

import dto
from ContentElementFacade import ContentElementFacade

from vulcan.clipanimator import ClipAnimator
from vulcan.typesetter import TextBubbleTypesetter, Font, CaptionTypesetter, TextAlignment
from vulcan.timeline import Timeline, TimelineEvent
import apollo_config as config
import dto_utils

# use the timeline to update timestamps for each text bubble and caption content element
def _update_caption_timestamps(  timeline : Timeline, meme : dto.Meme):
    pass


#
# this unnecessarily lengthy code simply gets the list of the specified number of
# timestamps for a content element and panel, calculates the durations, and returns
# a list of (timestamp,duration) tuples aka 'temporal data'
#
def _get_temporal_data(
        timeline : Timeline,
        panel_index,
        content_index,
        count):
    # find the panel
    t = list(timeline.enumerate_events(TimelineEvent.PANEL))[panel_index].t

    # find the content within the panel
    t = list(timeline.enumerate_events_relative(t, TimelineEvent.CONTENT))[content_index].t

    # get the list of timestamps
    s = list(timeline.enumerate_events_relative(t, TimelineEvent.WORD))[:count]
    timestamps = [row.t for row in s]
    last = timestamps[-1] if timestamps else t


    # calculation total duration for captions, which is the amount of time until the next word
    # or end of content, whichever comes first.  note this works for captions and text bubbles both
    # in a group or not.

    # duration is ignored for text being displayed as the child of another panel (text bubble) b/c
    # the duration is inherited from the parent panel
    t = timeline.calc_duration(last, TimelineEvent.WORD,  TimelineEvent.CONTENT_END)
    timestamps.append(last + t)

    # calculate durations
    t1 = np.array(timestamps)[:-1]
    t2 = np.array(timestamps[1:])
    durations = (t2 - t1).tolist()

    # return temporal data
    return list(zip(timestamps,durations))

# perform some necessary preprocessing on text bubbles in preparation for typesetting:
# + adjust bounding boxes to be relative to parent panel instead of the raw
# + normalize (make same size) font sizes if configured

def _preprocess_text_bubbles( timeline, meme : dto.Meme, panel_clips):
    typesetter = TextBubbleTypesetter(
        animator=None  # not needed for calculate_only
    )

    # size normalization
    font_sizes = []

    # adjust bounding boxes and calculate font sizes

    for i,panel in enumerate(meme.panels):
        for l,content in enumerate(panel.script):
            if content.text_bubble:
                tb = ContentElementFacade(meme,i,l)

                # the text bubble bounding box is relative to the raw, which was convenient for OCR.  however,
                # in order to create text relative to the parent panel, the bounding box needs to be relative
                # to the panel

                text_bubble_bb = dto_utils.bndbox_to_bbox(tb)
                text_bubble_bb = text_bubble_bb.translated(-panel.xmin, -panel.ymin)

                content.text_bubble.xmin = text_bubble_bb.xmin
                content.text_bubble.ymin = text_bubble_bb.ymin
                content.text_bubble.xmax = text_bubble_bb.xmax
                content.text_bubble.ymax = text_bubble_bb.ymax

                # for font size normalization
                if not content.text_bubble.font.size:
                    font = Font(tb.font.name if tb.font.name else config.TEXT_BUBBLE_FONT_NAME,
                                tb.font.size,
                                tb.font.color)


                    typesetter.show_bubble_text(
                        font=font,
                        parent_clip=panel_clips[i],
                        bbox=dto_utils.bndbox_to_bbox(tb),
                        text=tb.text,
                        alignment=TextAlignment.Left,
                        timestamps=_get_temporal_data(timeline, i,l, len(tb.timestamps)),
                        calculate_only=True)

                    if meme.header.font_size_normalization or config.FORGE_NORMALIZE_TEXT_BUBBLE_SIZE:
                        font_sizes.append(font.size)
                    else:
                        tb.font.size = font.size

    if ( meme.header.font_size_normalization or config.FORGE_NORMALIZE_TEXT_BUBBLE_SIZE) and font_sizes:

        match meme.header.font_size_normalization:
            case dto.FontSizeNormalizationType.MIN:
                estimated_size = min(font_sizes)

            case dto.FontSizeNormalizationType.MAX:
                estimated_size = max(font_sizes)

            case dto.FontSizeNormalizationType.MEAN:
                estimated_size = round(statistics.mean(font_sizes))

            case _: # default case, but python is too dumb to just call it that
                estimated_size = round(statistics.mean(font_sizes))


        for panel in meme.panels:
            for content in panel.script:
                if content.text_bubble and not content.text_bubble.font.size:
                    content.text_bubble.font.size = estimated_size


def typeset_captions(
                      timeline: Timeline,
                      meme: dto.Meme,
                      panel_clips,
                      animator: ClipAnimator,
                      caption_bb,
                      transitions):

    def get_first_value( *l ):
        return next((elem for elem in l if elem is not None), None)


    # 0 based speaker index to font
    # use the speaker font info in the meme, if provided.  otherwise use the FORGE_VOICE_TO_CAPTON_FONT dict in the ini
    # if neither of those were specified, just use the global default from the ini

    speaker_to_font = {}
    for i,speaker in enumerate(meme.header.speakers.speaker):
        tp = speaker.text_properties
        f: dto.FontType
        if speaker.voice in config.FORGE_VOICE_TO_CAPTION_FONT:
            f = config.FORGE_VOICE_TO_CAPTION_FONT[ speaker.voice]
        else:
            # adhoc voice, use defaults
            f = dto.FontType()

        font = Font(
            name= get_first_value(tp.name, f.name, config.CAPTION_FONT_NAME),
            size= get_first_value(tp.size, f.size, config.CAPTION_SIZE),
            color =get_first_value(tp.color, f.color, config.CAPTION_COLOR),
            stroke_width= get_first_value(tp.stroke_width, f.stroke_width,  config.CAPTION_STROKE_WIDTH),
            stroke_color= get_first_value(tp.stroke_color, f.stroke_color, config.CAPTION_STROKE_COLOR),
            highlight_color = get_first_value(tp.highlight_color, f.highlight_color, config.CAPTION_HIGHLIGHT_COLOR))


        speaker_to_font[i]=font

    for i, panel in enumerate(meme.panels):
        for l, content in enumerate(panel.script):
            tb = ContentElementFacade(meme,i,l)
            if tb.type == dto.ContentType.CAPTION:

                # content speaker number is 1 based, for *reasons*
                font = speaker_to_font[content.speaker-1]
                typesetter = CaptionTypesetter(animator, font, transitions) # making typesetter

                typesetter.show_captions( # do its thing
                    caption_bb,
                    tb.text,
                    _get_temporal_data(timeline, i,l, len(tb.timestamps)),
                    )


def typeset_text_bubbles(
        timeline : Timeline,
        meme : dto.Meme,
        panel_clips,
        animator : ClipAnimator,
        transitions ):

    _preprocess_text_bubbles(timeline,meme, panel_clips)

    typesetter = TextBubbleTypesetter(
        animator,
        transitions
    )

    for i, panel in enumerate(meme.panels):
        for l, content in enumerate(panel.script):
            if content.text_bubble:
                tb = ContentElementFacade(meme,i,l)

                highlight_color = tb.font.highlight_color if tb.font.highlight_color else config.TEXT_BUBBLE_HIGHLIGHT_COLOR
                if not highlight_color:
                    highlight_color = tb.font.color

                stroke_color = tb.font.stroke_color if tb.font.stroke_color else tb.font.color
                stroke_width = tb.font.stroke_width if tb.font.stroke_width else 1

                font = Font(tb.font.name if tb.font.name else config.TEXT_BUBBLE_FONT_NAME,
                            tb.font.size,
                            tb.font.color,
                            stroke_color,
                            stroke_width,
                            highlight_color)
                typesetter.show_bubble_text(
                    font,
                    panel_clips[i],
                    dto_utils.bndbox_to_bbox(tb),
                    tb.text,
                    # center text for text bubbles over images, since that is typically the alignment used in memes
                    TextAlignment.Left if tb.clean is not dto.CleanMethod.SMART else TextAlignment.Center,
                    _get_temporal_data(timeline, i,l, len(tb.timestamps)),
                    False)


