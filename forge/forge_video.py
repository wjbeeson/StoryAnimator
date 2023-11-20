from forge.clipanimator.clipanimator import easeOutBack, easeLinear
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
        font=font)  # making typesetter

    typesetter.show_captions(  # do its thing
        caption_bb,
        script,
        sync_values=sync_values,
        alignment=TextAlignment.Left)


def scroll_captions(animator, y_shift_line):
    clip_y_positions = _get_clip_y_positions(animator)
    first_y_level = clip_y_positions[0]
    if first_y_level > y_shift_line:
        raise Exception(
            f"Y Shift Line set too small: {y_shift_line}. Minimum size for current text size is {first_y_level}")

    for i, clip in enumerate(animator.clips):
        current_y_level = clip_y_positions[i]
        if current_y_level >= y_shift_line:

            # use the previous clip, so shift before it crosses the boundary
            previous_clip: VideoClip = animator.clips[i-1]
            start_time = previous_clip.start

            # use current clip so shift the next line all the way to the top
            current_clip: VideoClip = animator.clips[i]
            y_level = current_clip.position[1]
            shift_distance = y_level - first_y_level
            clip_y_positions = _shift_all_clips_up(animator, clip_y_positions, start_time, shift_distance)




def _shift_all_clips_up(animator, clip_y_positions, shift_start_time, shift_distance):
    for clip in animator.clips:
        clip:VideoClip
        animator.move_to(
            clip = clip,
            t_start=shift_start_time,
            t_end=shift_start_time + 3, #time to complete animation
            position=(0,-shift_distance),
            ease_fn=easeLinear,
            relative=True)
    new_y_positions=[]
    for y in clip_y_positions:
        new_position = y - shift_distance
        new_y_positions.append(new_position)
    return new_y_positions


def _get_clip_y_positions(animator):
    positions = []
    for clip in animator.clips:
        clip: VideoClip
        positions.append(clip.position[1])
    return positions

def write_video(animator, caption_bb, narration_file):
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
    background = (ColorClip(
        size=((int(caption_bb.size[0]),int(caption_bb.size[1]))),
        color=(27, 18, 18))
                  .set_position((int(caption_bb.xmin), int(caption_bb.ymin)))
                  .set_opacity(0.7))
    video = CompositeVideoClip([clip, background, *animator.clips])

    # write video
    video.set_duration(probe_audio(narration_file)).write_videofile("flower.mp4")

    # concatenate with audio
    input_video = ffmpeg.input("flower.mp4")
    input_audio = ffmpeg.input(narration_file)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output("temp/test.mp4").overwrite_output().run()


def probe_audio(audio_file):
    probe = ffmpeg.probe(audio_file)
    stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = float(stream['duration'])
    return (duration)