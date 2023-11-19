from abc import ABC
import numpy as np

class ClipMutatorDigitized(ABC):
    def __init__(self):
        self._time_to_mutator = {}
        self._clip = None

    def lookup_mutator(self,t):
        # first get a sorted list of t,mover pairs
        l = sorted(list(self._time_to_mutator.items()),key=lambda e: e[0])

        # split into two lists
        bins, mutators = list(zip(*l))
        i = np.digitize(t, bins)
        mutator = mutators[i-1]
        return mutator

    def __call__(self,t):
        raise NotImplementedError()

    def set_clip(self, clip):
        self._clip = clip

    def add_mutator(self, t, mutator=None):
        # allow the default stationary at t==0 to be overwritten
        if t not in self._time_to_mutator or self._time_to_mutator[t] is None:
            self._time_to_mutator[t] = mutator
        else:
            assert False, f"Mutator already scheduled for time {t}"