import numpy as np


class ClipMoverRelative:
    def __init__(self,start_time, fn, one_shot=False):
        self._fn = fn
        self._one_shot = one_shot
        self._triggered = False # only used when one_shot==True
        self._start_position = None
        self._start_time = start_time
    def __call__(self, clip, t):
        # init
        if not self._start_position:
            self._start_position = clip.position

        if self._one_shot:
            if self._triggered:
                return clip.position
            else:
                self._triggered = True

        clip.position = self._fn(t - self._start_time, self._start_position)

        return clip.position


class ClipMoverTo:
    def __init__(self, start_time, t, position, ease_fn, relative):
        self._arrive_at = t
        self._target_position = position
        self._relative = relative
        self._t_start = start_time
        self._dt = self._arrive_at - self._t_start

        if ease_fn != None:
            self._ease_fn = ease_fn
        else:
            ease_fn = lambda t: t

        # initialized during first __call__
        self._dx = None
        self._dy = None

    def __call__(self,clip,t):
        if self._dx is None:
            # initialize

            if self._relative:
                self._target_position = tuple(np.array(clip.position) + np.array(self._target_position))

            self._dx = self._target_position[0] - clip.position[0]
            self._dy = self._target_position[1] - clip.position[1]
            self._dx = (self._target_position[0] - clip.position[0])/self._dt
            self._dy = (self._target_position[1] - clip.position[1])/self._dt
            self._start_position = clip.position

        if t > self._arrive_at:
            clip.position = self._target_position # animation duration reached, just return final position
        else:
            clip.position = (
                                self._start_position[0] + self._dx * (t-self._t_start) * self._ease_fn( (t-self._t_start)/self._dt),
                             self._start_position[1] + self._dy * (t-self._t_start) * self._ease_fn((t-self._t_start)/self._dt))



        return clip.position




class ClipMoverChild:

    def __init__(self, parent_positioner, offset, deltat):
        self._parent_positioner = parent_positioner
        self._offset = offset
        self._deltat = deltat

    def __call__(self,clip,t):
        parent_pos = self._parent_positioner(t+self._deltat)
        pos = np.add(parent_pos, self._offset)
        return pos


