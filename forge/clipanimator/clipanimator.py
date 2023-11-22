

from moviepy.editor import *
from moviepy import Clip



from .clippositioner import ClipPositionerDigitized
from .clipmovers import ClipMoverRelative, ClipMoverChild, ClipMoverTo
from .clipsizer import ClipSizerDigitized, ClipSizerSinWave, ClipSizerZoom
from .ease_functions import easeLinear, easeOutBack

from .transitioneffecttype import TransitionEffectType

def hash_hack(self):
    return id(self)
VideoClip.__hash__ = hash_hack
ColorClip.__hash__ = hash_hack

def resize_popup(t):
   x = min(1,t/.3 * .90 + .1)
   x= easeOutBack(x)
   return x


#
# modify the set_position method of the various Clip subclasses to monkey patch
# a new property called 'position' that stores the specified value.  only makes
# sense for positions specified as numeric tuples e.g. (100,50)
#

def set_position_decorator(fn):
    def wrapper(*args, **kwargs):
        new_clip = fn(*args,**kwargs)

        # only store the position if it is actually a (x,y) position value.  otherwise, the
        # position will be overwritten with the lambda
        if type(args[1])==tuple:
            new_clip.position = args[1]
        return new_clip

    return wrapper

VideoClip.set_position = set_position_decorator(VideoClip.set_position)

# the purpose of this decorator is to prevent my position attribute from being lost when
# any clip operation such as set_duration causes a copy to be made.
def copy_decorator(fn):
    def wrapper(*args,**kwargs):
        new_clip = fn(*args,**kwargs)

        # if the original clip had my position field, propagate to the copy.
        if hasattr(args[0],'position'):
            new_clip.position = args[0].position

        return new_clip

    return wrapper

Clip.copy = copy_decorator(Clip.copy)


class ClipAnimator:

    def __init__(self, screen_size):
        self._clip_to_positioner = {}
        self._clip_to_sizer = {}
        self.SCREEN_SIZE = screen_size

    @property
    def clips(self):
        return list(self._clip_to_positioner.keys())

    def add_child_clip(self, parent, clip, relative_pos, transition_in=None, transition_out=None):

        assert transition_out is None or transition_out == TransitionEffectType.FADE

        # child inherits parent's duration if not specified
        if not clip.duration:
            duration = parent.duration + parent.start - clip.start
            #assert duration > 0
            clip = clip.set_duration(duration)

        p = ClipPositionerDigitized()
        p.add_mutator(
            0,
            ClipMoverChild(
                self._clip_to_positioner[parent],
                relative_pos,
                clip.start - parent.start))

        if transition_out and transition_out.value &  TransitionEffectType.FADE.value:
            clip = vfx.fx.all.fadeout(clip, .5)
        # need to call set_position first in order to get new clip, then store in dict
        clip = clip.set_position(p)

        if transition_in != None:
            if transition_in.value & TransitionEffectType.POP.value:
                initial_size = clip.size
                clip = clip.resize(resize_popup)

                clip.size = initial_size

            # TODO: investigate why FADE prevents POP from rendering correctly.
            if transition_in.value & TransitionEffectType.FADE.value:
                clip = vfx.fx.all.fadein( clip, .5 )


        self._clip_to_positioner[clip] = p

        if transition_in != None  and transition_in.value & TransitionEffectType.POP.value:
            self._clip_to_positioner[clip]._adjust_pos_fn = \
                lambda new_pos, t: self._adjust_pos_fn(t, initial_size[0], initial_size[1], resize_popup, new_pos, transition_in)

        return clip

    def add_clip(self, clip, transition_in=None, transition_out=None):

        assert hasattr(clip,'position'),'Call set_position prior to adding clip'
        assert transition_out is None or transition_out == TransitionEffectType.FADE

        clip_positioner = ClipPositionerDigitized()
        clip_positioner.add_mutator(0)

        clip_sizer = ClipSizerDigitized()
        clip_sizer.add_mutator(0)

        if transition_out and transition_out.value &  TransitionEffectType.FADE.value:
            clip = vfx.fx.all.fadeout(clip, .5)
        # need to call set_position first in order to get new clip, then store in dict
        clip = clip.set_position(clip_positioner)
        clip = clip.resize(clip_sizer)

        if transition_in != None:
            if transition_in.value & TransitionEffectType.POP.value:
                initial_size = clip.size
                clip = clip.resize(resize_popup)

                clip.size = initial_size

            # TODO: investigate why FADE prevents POP from rendering correctly.
            if transition_in.value & TransitionEffectType.FADE.value:
                clip = vfx.fx.all.fadein( clip, .5 )

        clip_positioner.set_clip(clip)
        clip_sizer.set_clip(clip)
        self._clip_to_positioner[clip] = clip_positioner
        self._clip_to_sizer[id(clip)] = clip_sizer

        if transition_in != None  and transition_in.value & TransitionEffectType.POP.value:
            self._clip_to_positioner[clip]._adjust_pos_fn = \
                lambda new_pos, t: self._adjust_pos_fn(t, initial_size[0], initial_size[1], resize_popup, new_pos, transition_in)

        return clip


    # move the specified clip once, relative to its current position

    def move(self,clip,/,t,deltax,deltay, one_shot = True):



        if clip not in self._clip_to_positioner:
            raise Exception("Call add_clip first and update clip reference with the result.")

        # start time and end time are given in segment time, not clip time which starts from 0
        t -= clip.start

        if not one_shot:
            fn = lambda t2, pos: (pos[0] + deltax * t2, pos[1] + deltay * t2)
        else:
            fn = lambda t2, pos: (pos[0] + deltax, pos[1] + deltay)

        self._clip_to_positioner[clip].add_mutator(
            t,
            ClipMoverRelative(t, fn, one_shot=one_shot))



    def move_to(self, clip, t_start, t_end, position, ease_fn, relative=False):
        if clip not in self._clip_to_positioner:
            raise Exception("Call add_clip first and update clip reference with the result.")

        # start time and end time are given in segment time, not clip time which starts from 0
        t_start -= clip.start

        self._clip_to_positioner[clip].add_mutator(
            t_start,
            ClipMoverTo(t_start, t_end-clip.start, position, ease_fn, relative)
        )

    def move_with(self, clip, anchor_clip, start_time, offset  ):

        start_time -= clip.start

        self._clip_to_positioner[clip].add_mutator(
            start_time,
            ClipMoverChild(
                self._clip_to_positioner[anchor_clip],
                offset,
                clip.start - anchor_clip.start)
        )


    def pulsate_at(self,clip, period, scale, offset, start_time, duration ):
        assert clip in self._clip_to_sizer

        start_time -= clip.start

        self._clip_to_sizer[clip].add_mutator(
            start_time,
            ClipSizerSinWave(
                period = period,
                shift = offset,
                scale = scale
            )
        )

    def zoom(self, clip, start_time, duration, start_scale, end_scale, ease_fn = easeLinear ):
        assert clip in self._clip_to_sizer

        start_time -= clip.start
        self._clip_to_sizer[clip].add_mutator(
            start_time,
            ClipSizerZoom(
                start_scale=start_scale,
                end_scale = end_scale,
                start_time = start_time,
                duration = duration,
                ease_fn = ease_fn
            )
        )


    def pan_n_zoom(self, clip, start_time, pos, duration=2,  start_scale=1, end_scale=3,ease_fn=easeLinear ):
        self.zoom(
            clip=clip,
            start_time = start_time,
            duration = duration,
            start_scale = start_scale,
            end_scale=end_scale,
            ease_fn= easeLinear)

        self.move_to(
            clip=clip,
            t_start= start_time,
            t_end=start_time + duration,
            ease_fn=ease_fn,
            position=pos,
            relative=False
        )

        # flyoff

        x,_ = self.SCREEN_SIZE
        x += int(clip.w)
        y = -int(clip.h)

        self.move_to(
            clip=clip,
            t_start= start_time + clip.duration-.5,
            t_end=start_time + clip.duration,
            ease_fn=ease_fn,
            position=(x,y),
            relative=False
        )




    def _adjust_pos_fn(self, t, w, h, resize_fn, pos, transition ):

        if t < 0:
            breakpoint()
        scale = resize_fn(t)

        if transition == TransitionEffectType.POP:
            dx = w/2 - w * scale /2
            dy = h/2 - h * scale /2
        elif transition == TransitionEffectType.POP_LEFT:
            dx = 0
            dy = 0
        else: # POP_RIGHT
            dx = w - w * scale
            dy = h - h * scale

        x,y = pos
        return x + dx, y + dy





