from forge.clipanimator.clipanimator import *
from matplotlib.transforms import Bbox
from forge.typesetter import *

# Import everything needed to edit video clips
def typeset_captions(
        animator: ClipAnimator,
        font,
        caption_bb: Bbox,
        script,
        sync_values
):

    typesetter = CaptionTypesetter(
        animator=animator,
        font=font) # making typesetter

    typesetter.show_captions( # do its thing
        caption_bb,
        script,
        sync_values=sync_values)
'''
from moviepy.editor import *

# loading video dsa gfg intro video  
clip = VideoFileClip("C:\\Users\\wjbee\\Desktop\\burning-tree-stunning-flames-SBV-346704080-HD.mp4")

# clipping of the video   
# getting video for only starting 10 seconds  
clip = clip.subclip(0, 10)

# Generate a text clip  
txt_clip = TextClip("Hello World", fontsize=75, color='black')

# setting position of text in the center and duration will be 10 seconds  
txt_clip = txt_clip.set_position('center').set_duration(10)

# Overlay the text clip on the first video clip  
video = CompositeVideoClip([clip, txt_clip])

# showing video  
video.set_duration(10).write_videofile("flower.mp4")
'''