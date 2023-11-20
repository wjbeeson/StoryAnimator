from dataclasses import dataclass
from matplotlib.transforms import Bbox
from moviepy.editor import *
import numpy as np


from vulcan.clipanimator import ClipAnimator, TransitionEffectType, easeOutBack, easeOutCubic, easeLinear
import vulcan.zones as zones
import apollo_config as config
from vulcan.soundboard import SoundSFXType, SoundBoard
@dataclass
class FeatureAnimationParams:
    animator: ClipAnimator
    zone: Bbox
    screen_size : (int ,int)
    raw_data : np.array
    positions: list[(int, int)]
    panels: list[ImageClip]
    margin : int
    crawl_speed : float
    temporal_params: list[(float, float, float, float)]  # (start,Duration,animation_start,animation_end)
    transitions: (TransitionEffectType, TransitionEffectType)  # in/out


def animate_panels_sequential(
        params: FeatureAnimationParams,
        direction: str,
        fn_offset):

    audio_clips = []

    # scale to the aggregate size of the largest panel
    scale = zones.calculate_scale( params.zone.size,
                                   (max([p.w for p in params.panels]) ,max([p.h for p in params.panels])),
                                   max_scale = config.FORGE_MAX_RAW_UPSCALE_FACTOR)

    params.margin *= scale

    # need two passes thru the panels, to make sure each panel has its new rescaled size for subsequent
    # layout calculations

    panel_positions = []

    # first pass, recalibrate each panel and add to animator
    for i in range(len(params.panels)):
        clip_start, clip_duration,  animation_end = params.temporal_params[i]

        clip_start -= .5

        # position panels just off the bottom of the screen

        clip = params.panels[i].set_start(clip_start) \
            .set_duration(clip_duration) \
            .resize(scale)

        x ,y = params.zone.align(clip.size, 1.0, direction) # scale = 1 since panel was resized
        pt = (int(x) ,int(y))
        clip = clip.set_position((int(x) ,params.screen_size[1 ] -clip.h))
        params.panels[i] = params.animator.add_clip(clip, transition_in=params.transitions[0], transition_out=params.transitions[1])

        panel_positions.append(pt)

        # quickly move to start location
        params.animator.move_to(
            params.panels[i],
            clip_start , # when panel appears
            clip_start +.5, # when panel reaches final destination
            pt,
            lambda t: t,
            relative=False)

        # first panel crawls, remaining panels follow the one above them
        if i == 0:
            params.animator.move(
                params.panels[i],
                clip_start +.5,
                0,
                - params.crawl_speed,
                False )
        else:
            x = params.panels[i].position[0] - params.panels[i-1].position[0]
            y = params.panels[i-1].h

            params.animator.move_with(
                params.panels[i],
                params.panels[ i -1],
                clip_start +.5,
                (x ,y)
            )

        audio_clips.append(
            SoundBoard[SoundSFXType.PANEL_APPEAR].set_start( clip_start)
        )

    # second pass, animate the panels
    for i in range(len(params.panels ) -1):
        clip_start, clip_duration,  animation_end = params.temporal_params[i]

        panel_positions[0] = np.add(panel_positions[0] ,fn_offset(params.animator.clips, i))

        params.animator.move_to(
            params.animator.clips[0],
            animation_end - .3,
            animation_end,
            panel_positions[0],
            lambda t: t,
            relative=False)

        # crawl

        params.animator.move(
           params.animator.clips[0],
           animation_end,
           0,
           -params.crawl_speed,
           False)

        clip =  SoundBoard[SoundSFXType.PANEL_MOVE].set_start(animation_end - .3)
        multiplier = clip.duration / .3

        # speed up clip to fit time window
        # todo: add this to soundboard
        # bugbug: not working for some reason, for now just transform asset directly
        #         clip = clip.fl_time(lambda t: multiplier * t, apply_to=['mask', 'audio'])
        audio_clips.append(clip)

    # flyoff

    _ ,_ ,animation_end = params.temporal_params[-1]
    flyoff_start = animation_end - config.FORGE_FLYOFF_SECS_FROM_END - config.FORGE_FLYOFF_DURATION
    flyoff_end = animation_end - config.FORGE_FLYOFF_SECS_FROM_END

    panel_positions[0] = np.add( panel_positions[0], (0 ,-params.screen_size[1]))

    params.animator.move_to(
        params.animator.clips[0],
        flyoff_start,
        flyoff_end,
        panel_positions[0],
        easeOutCubic,
        relative=False )

    clip = SoundBoard[SoundSFXType.PANEL_MOVE].set_start(flyoff_start)
    audio_clips.append(clip)

    return audio_clips ,scale

def animate_panels_build_from_right(params: FeatureAnimationParams):
    return animate_panels_sequential(params, 'r', lambda panels, i:
    (-panels[min(i + 1, len(params.panels) - 1)].w - params.margin, 0))


def animate_panels_build_from_left(params: FeatureAnimationParams):
    return animate_panels_sequential(params, 'l', lambda panels, i: (
    panels[min(i + 1, len(params.panels) - 1)].w + params.margin, 0))


def animate_panels_build_from_top(params: FeatureAnimationParams):
    return animate_panels_sequential(params, 't', lambda panels, i: (
    0, panels[min(i + 1, len(params.panels) - 1)].h + params.margin))


def animate_panels_build_from_bottom(params: FeatureAnimationParams):
    return animate_panels_sequential(params, 'b', lambda panels, i: (
    0, -panels[min(i + 1, len(params.panels) - 1)].h - params.margin))


LANDSCAPE_FEATURE_ANIMATIONS = [animate_panels_build_from_right]
PORTRAIT_FEATURE_ANIMATIONS = [animate_panels_build_from_bottom]


def animate_panels_in_place(params: FeatureAnimationParams):
    audio_clips = []

    # scale to the aggregate size of the largest panel
    scale = zones.calculate_scale(params.zone.size, params.raw_data.size,
                                  max_scale=config.FORGE_MAX_RAW_UPSCALE_FACTOR)

    offset = params.zone.align(params.raw_data.size, scale, 'cc')

    start_positions = []

    for i in range(len(params.panels)):
        pt = zones.transform_point(params.positions[i], scale, offset)
        start_positions.append(pt)
        clip_start, clip_duration, animation_end = params.temporal_params[i]
        # fly on
        clip_start -= .5

        # position panels just off the bottom of the screen

        # experimental change to allow scaling w/o introducing gaps
        import math
        # scale by raw and apply ceiling to avoid gaps between panels
        w = math.ceil(params.panels[i].w * scale)
        h = math.ceil(params.panels[i].h * scale)

        clip = params.panels[i].set_start(clip_start) \
            .set_duration(clip_duration) \
            .resize((w, h))

        clip = clip.set_position((pt[0], params.screen_size[1] - clip.h))
        params.panels[i] = params.animator.add_clip(clip, transition_in=params.transitions[0],
                                                    transition_out=params.transitions[1])

        # quickly move to start location
        params.animator.move_to(
            params.panels[i],
            clip_start + .0001,  # fudge the start time to workaround a limitation in clipanimator
            clip_start + .5,
            pt,
            easeOutBack,
            relative=False)

        audio_clips.append(
            SoundBoard[SoundSFXType.PANEL_APPEAR].set_start(clip_start)
        )

    # flyoff
    for i in range(len(params.panels)):
        flyoff_start = animation_end - config.FORGE_FLYOFF_SECS_FROM_END - config.FORGE_FLYOFF_DURATION
        flyoff_end = animation_end - config.FORGE_FLYOFF_SECS_FROM_END

        h = params.panels[i].h
        pos = start_positions[i]

        params.animator.move_to(
            params.animator.clips[i],
            flyoff_start,
            flyoff_end,
            (pos[0], -h),
            easeOutCubic,
            relative=False)

        clip = SoundBoard[SoundSFXType.PANEL_MOVE].set_start(flyoff_start)
        audio_clips.append(clip)

    return audio_clips, scale

