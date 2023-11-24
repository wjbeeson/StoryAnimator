import numpy as np

from forge.clipanimator.clipanimator import easeOutBack, easeLinear
from matplotlib.transforms import Bbox
from forge.typesetter import *
from moviepy.editor import *
from pydub import AudioSegment
import ffmpeg
from moviepy.video.tools.drawing import color_gradient
from datetime import datetime
from PIL import Image
from matplotlib import cm

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

    positions = typesetter.show_captions(  # saves positions to check where they are later. Useful for dynamic edits
        caption_bb,
        script,
        sync_values=sync_values,
        total_duration=probe_audio(narration_file),
        alignment=TextAlignment.Left)

    return positions

def scroll_captions(animator, y_shift_line, positions):
    clip_y_positions = _get_clip_y_positions(positions)
    first_y_level = clip_y_positions[0]
    if first_y_level > y_shift_line:
        raise Exception(
            f"Y Shift Line set too small: {y_shift_line}. Minimum size for current text size is {first_y_level}")

    for i in range(len(animator.clips) - 1): #minus one to remove the parent clip
        current_y_level = clip_y_positions[i]
        if current_y_level >= y_shift_line:

            # use the previous clip, so shift before it crosses the boundary
            previous_clip: VideoClip = animator.clips[i-2] # going back by two to get to a highlight clip
            start_time = previous_clip.start

            # use current clip so shift the next line all the way to the top
            shift_distance = current_y_level - first_y_level
            clip_y_positions = _shift_all_clips_up(animator, clip_y_positions, start_time, shift_distance)




def _shift_all_clips_up(animator, clip_y_positions, shift_start_time, shift_distance):
    parent_clip = animator.clips[0]

    parent_clip: VideoClip
    animator.move_to(
        clip = parent_clip,
        t_start=shift_start_time,
        t_end=shift_start_time + 3, #time to complete animation
        position=(0, -shift_distance),
        ease_fn=easeLinear,
        relative=True)

    new_y_positions=[]
    for y in clip_y_positions:
        new_position = y - shift_distance
        new_y_positions.append(new_position)
    return new_y_positions


def _get_clip_y_positions(positions):
    y_positions = []
    for position in positions:
        y_positions.append(position[1])
    return y_positions

def write_video(animator, caption_bb, narration_file, background_clip,screen_size):
    # Step 1: Create composite of captions and add the mask
    caption_comp = CompositeVideoClip([*animator.clips],size=screen_size)  # make composite from captions only
    mask = create_gradient_mask(screen_size, caption_bb, duration=probe_audio(narration_file))

    # fl = lambda pic: np.minimum(pic, gradmask.img)
    def make_mask_transparent(pic):
        return np.minimum(pic, mask.img)

    caption_comp.mask = caption_comp.mask.fl_image(make_mask_transparent)
    #caption_comp.set_duration(probe_audio(narration_file)).write_videofile("temp/caption_test.mp4",fps=30)
    #breakpoint()

    # Step 2: Combine captions with background
    backdrop = (ColorClip(
        size=((int(screen_size[0] - 2 * caption_bb.xmin),int(screen_size[1] - 2 * caption_bb.ymin))),
        color=(27, 18, 18))
                  .set_position((int(caption_bb.xmin), int(caption_bb.ymin)))
                  .set_opacity(0.7))
    video = CompositeVideoClip([background_clip, backdrop, caption_comp]) # remove and apply gradient mask

    # Step 3: Write Video
    print(f"Start: {datetime.now()}")
    video.set_duration(probe_audio(narration_file)).write_videofile("temp/feature_nosound.mp4",fps=60)
    print(f"End: {datetime.now()}")

    # Step 4: Add Audio
    input_video = ffmpeg.input("temp/feature_nosound.mp4")
    input_audio = ffmpeg.input(narration_file)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output("temp/feature.mp4").overwrite_output().run()

def probe_audio(audio_file):
    probe = ffmpeg.probe(audio_file)
    stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    duration = float(stream['duration'])
    return (duration)

def create_gradient_mask(screen_size, caption_bb:Bbox, duration):
    # bugbug: this code requires the following modification in moviepy drawing.py:147
    # if vector is not None:
    #     norm = np.linalg.norm(vector)

    cx = int(screen_size[0])
    cy = int(screen_size[1])
    top = caption_bb.ymin
    gradient_top = color_gradient(
        size=(cx, cy),
        p1=(0, top - 25),
        p2=(0, top + 25),
        col1=1.0,
        col2=0
    )

    bottom = cy - top
    gradient_bottom = color_gradient(
        size=(cx, cy),
        p1=(0, bottom - 25),
        p2=(0, bottom + 25),
        col1=0,
        col2=1.0
    )

    combined_gradient = np.minimum(gradient_top, gradient_bottom)
    mask_clip = ImageClip(combined_gradient, ismask=True).set_duration(duration)

    # test code
    #test_image = Image.fromarray(np.uint8(cm.gist_earth(combined_gradient) * 255))
    #test_image.show()
    #breakpoint()
    return mask_clip

