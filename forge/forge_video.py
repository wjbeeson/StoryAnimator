from forge.clipanimator.clipanimator import *
from matplotlib.transforms import Bbox
from forge.typesetter import *
from moviepy.editor import *
from pydub import AudioSegment
import ffmpeg

# Import everything needed to edit video clips
def typeset_captions(
        animator: ClipAnimator,
        font,
        caption_bb: Bbox,
        script,
        sync_values,
        narration_file
):

    typesetter = CaptionTypesetter(
        animator=animator,
        font=font) # making typesetter

    typesetter.show_captions( # do its thing
        caption_bb,
        script,
        sync_values=sync_values,
        alignment=TextAlignment.Left)



    # loading video dsa gfg intro video
    clip = VideoFileClip("C:\\Users\\wjbee\\Desktop\\burning-tree-stunning-flames-SBV-346704080-HD.mp4")

    # clipping of the video
    # getting video for only starting 10 seconds
    clip = clip.subclip(0, 10)

    # Generate a text clip
    #txt_clip = TextClip("Hello World", fontsize=75, color='black')

    # setting position of text in the center and duration will be 10 seconds
    #txt_clip = txt_clip.set_position('center').set_duration(10)

    # Overlay the text clip on the first video clip
    breakpoint()
    background = (ColorClip(
        size=((int(caption_bb.size[0]),int(caption_bb.size[1]))),
        color=(27, 18, 18))
                  .set_position((int(caption_bb.xmin), int(caption_bb.ymin)))
                  .set_opacity(0.7))
    video = CompositeVideoClip([clip, background, *animator.clips])

    # showing video
    video.set_duration(10).write_videofile("flower.mp4")
    import ffmpeg

    input_video = ffmpeg.input("flower.mp4")

    input_audio = ffmpeg.input(narration_file)

    ffmpeg.concat(input_video, input_audio, v=1, a=1).output("temp/test.mp4").overwrite_output().run()

