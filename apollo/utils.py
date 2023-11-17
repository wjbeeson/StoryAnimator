import random

import numpy as np
from moviepy.editor import *
from vulcan.pydubclip import PydubClip
from PIL import Image, ImageDraw
from matplotlib.transforms import Bbox
import pandas as pd
import cv2
import statistics

from vulcan.detextify.detextifier import DetextifierTextbox
from vulcan.detextify.inpainter import CustomDalleInpainter
from vulcan.detextify.annotation_parser import TextBox, get_textbox
from PIL import Image
import numpy as np
import os
from pathlib import Path


import dto
import dto_utils
from ContentElementFacade import ContentElementFacade
import apollo_config as config


def read_slices(filename, slice_type=int):
    with open(filename) as f:
        return list(map(slice_type, f.read().split(',')))

def audio_clips_from_slice(src, slices):
    return [src.subclip(slices[i] - .1, slices[i] + .1) for i in range(len(slices))]


#
# create an audio clip for each line of narration, and group them by panel
# for easier processing
#
# the structure is:
#   [ [(clip,duration), (clip,duration)],   # panel 0
#     [(clip,duration)],                    # panel 1
#   ]
#
# the purpose of including the durations is a content_element be declared
# with the 'duration' attribute, which overrides the actual narration duration.
# this is required for picture panels, and may have other uses
#

def create_narration_clips( meme, meme_path, ce_groups ):
    clip_groups = []

#    (panel_index, line_num, list[content_index])]
    for panel_index, line_num, content_nums in ce_groups:
        if not len(clip_groups) > panel_index:
            clips = []
            clip_groups.append(clips)

        duration = None

        try:
            clip = PydubClip(f"{meme_path.parent/meme_path.stem}_{panel_index}_{line_num}.wav")
        except OSError as x:
            # this error results from the empty .wav that is generated for 'slice-only' messages
            # with no text.  i hack around this my creating a very short silent clip
            if "failed to read the duration" in str(x):
                clip=AudioClip( lambda t: 0, duration = .1)

        duration = clip.duration

        # allow duration to be adjusted for content elements not part of a group
        if len(content_nums)==1:
            ce = ContentElementFacade(meme,panel_index,content_nums[0])

            # picture panels have a special default duration to avoid the need to specify
            # each time
            if ce.type == dto.ContentType.PICTURE:
                duration = config.TIMELINE_PICTURE_PANEL_DURATION

            # note: i interpret the Duration attribute as an *adjustment* to the narration duration, not
            # an absolute value.  the reason is i think it's more likely the editor will want to increase or
            # decrease an element duration than to know the exact desired value.  also, for the case of pictures
            # which have a 0 duration by default, the adjusted duration *is* the absolute duration.

            if ce.duration : duration += ce.duration

        clips.append((clip,duration))

    return clip_groups

def durations_from_timestamps( timestamps, final_duration ):
    durations = np.subtract( timestamps[1:], timestamps[:-1])
    return np.append( durations, final_duration).tolist()


def cut_panels( raw_image, bb_list ):
    for bb in bb_list:
        x1,y1,x2,y2 = bb.get_points().flatten().astype('int')
        pt = (x1,y1)
        panel_data = raw_image[y1:y2,x1:x2,:]


        yield pt, panel_data



def bb_from_bndbox_list( l ):
    bb_list = []
    for bndbox in l:
        bb_list.append(Bbox([  [bndbox.xmin,bndbox.ymin],   [bndbox.xmax,bndbox.ymax]]))


    return bb_list

def clean_raw(raw_image, meme):


    #
    # cleaning is done in two passes.  first solid cleaning is performed, one text bubble
    # at time.  next, all smart/inpainting cleaning is done in one shot
    #

    # accumulates inpainting bb's
    text_boxes = []

    # first two solid cleaning, while keeping track of inpainting bb's
    draw = ImageDraw.Draw(raw_image)
    for i,panel in enumerate(meme.panels):
        for l,content in enumerate(panel.content):
            ce = ContentElementFacade(meme,i,l)
            match ce.clean:
                case dto.CleanMethod.SOLID:
                    draw.rectangle( [ce.xmin, ce.ymin, ce.xmax, ce.ymax], fill=ce.background)

                case dto.CleanMethod.SMART:
                    text_boxes.append(get_textbox(x1=ce.xmin, y1 = ce.ymin, x2 = ce.xmax, y2 = ce.ymax))

                case dto.CleanMethod.NONE:
                    pass

    image_data = np.array(raw_image)

    # now do the inpainting
    if text_boxes:
        detextify = DetextifierTextbox(CustomDalleInpainter())
        image_data = detextify.detextify(text_boxes, np.array(raw_image))

    img = Image.fromarray(image_data)
    return img


def frange( start, count, step ):
    return np.add(start,np.multiply(step,  range(0,count)))

def slice_img_data(self : Bbox, img_data ):
    x1,y1,x2,y2 = self.get_points().astype('int').flatten()

    return img_data[y1:y2,x1:x2,:]

Bbox.slice = slice_img_data

#
# todo: need a higher level function that detects colors across multiple boxes and returns the most commonly
# detected value
#



# todo: this doesn't appear to work for b/w images
def shrink_bb_to_image( self, image_data, border=0):
    image_data = self.slice(image_data)
    image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(image_data, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    # Get the tight bounding box by finding the minimum and maximum x and y values
    x, y, w, h = np.min([b for b in bounding_boxes], axis=0)
    x_max, y_max = np.max(np.array(bounding_boxes)[:, 2:] + np.array(bounding_boxes)[:, :2], axis=0)

    bbox_tight = Bbox([[x,y],[x_max,y_max]])


    return bbox_tight.translated(self.xmin, self.ymin).padded( border )

Bbox.tighten = shrink_bb_to_image

