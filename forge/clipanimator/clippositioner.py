from .clipmutator import ClipMutatorDigitized


class ClipPositionerDigitized( ClipMutatorDigitized):
    def __call__(self, t):
        m = self.lookup_mutator(t)
        if m:
            new_pos = m(self._clip,t)
        else:
            new_pos = self._clip.position


        if hasattr( self, '_adjust_pos_fn'):
            new_pos = self._adjust_pos_fn(new_pos,t)

        return new_pos

