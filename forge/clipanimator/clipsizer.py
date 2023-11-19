import math

from .clipmutator import ClipMutatorDigitized


class ClipSizerDigitized( ClipMutatorDigitized):
    def __call__(self, t):
        m = self.lookup_mutator(t)
        if m:
            new_size = m(self._clip,t)
        elif self._clip:
            new_size = 1.0
            #new_size = self._clip.size
        else:
             new_size = 1.0

        return new_size


class ClipSizerSinWave:
    def __init__(self, period, shift, scale):
        self._period = period
        self._shift = shift
        self._scale = scale
    def __call__(self, clip, t ):

        rads = (t+self._shift) / self._period * math.pi
        return math.sin(rads) * self._scale + 1.0


class ClipSizerZoom:
    def __init__(self, start_scale, end_scale, start_time, duration, ease_fn ):
        self._start_scale = start_scale
        self._end_scale = end_scale
        self._start_time = start_time
        self._duration = duration
        self._ease_fn = ease_fn

    def __call__(self, clip, t ):
        return min(self._end_scale,self._start_scale + (self._end_scale - self._start_scale) * t/(self._start_time + self._duration)\
            * self._ease_fn((t-self._start_time)/self._duration))


