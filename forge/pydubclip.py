from pydub import AudioSegment
from pathlib import Path
class PydubClip():
    def __init__(self, filename):
        self._as : AudioSegment
        self._start : float

        # save the filename for clones
        self._filename = filename

        self._start = 0.0

        if filename:
            match Path(filename).suffix.lower():
                case ".wav":
                    self._as = AudioSegment.from_wav(filename)

                case ".mp3":
                    self._as = AudioSegment.from_mp3(filename)

                case _:
                    raise ValueError(f"Unsupported file type {Path(filename).suffix}")
        else:
            self._as = None

    def __str__(self):
        return f"PydubClip(duration={self.duration})"

    def subclip(self, start, duration=None):
        new_clip = PydubClip(None)
        if duration:
            new_clip._as = self._as[start*1000:(start+duration)*1000]
        else:
            new_clip._as = self._as[start*1000:]

        new_clip._start = self._start
        return new_clip

    def set_start(self, t):

        new_clip = PydubClip(self._filename)
        if not self._filename:
            # hopefully this will clone the clip
            new_clip._as = self._as + 0.0
        new_clip._start = t

        return new_clip

    @property
    def start(self):
        return self._start

    @property
    def duration(self):
        return self._as.duration_seconds

    def set_start(self, t):

        new_clip = PydubClip(self._filename)
        if not self._filename:
            # hopefully this will clone the clip
            new_clip._as = self._as + 0.0
        new_clip._start = t

        return new_clip

    def volumex(self, dbs):
        new_clip = PydubClip(None)
        new_clip._as = self._as + dbs
        new_clip._start = self._start

        return new_clip

    def loop(self, duration):

        if duration / self.duration >= 2:
            new_clip = PydubClip(None)
            new_clip._start = self._start
            new_clip._as = self._as * int(duration / self.duration)
        else:
            new_clip = self

        return new_clip
    @classmethod
    def from_overlays(cls, duration, overlay_clips ):

        combined = AudioSegment.silent( duration * 1000)

        # perform the overlay
        for overlay_clip in overlay_clips:

            # ignore placeholder audio for picture panels
            if overlay_clip.duration == 0:
                continue

            # can get negative values for start if leader is reduced or eliminated, and so pydub will interpret
            # the duration from the *end* of the clip
            start = overlay_clip.start if overlay_clip.start >= 0 else 0

            combined= combined.overlay( overlay_clip._as, position = start * 1000)

        new_clip = PydubClip(None)
        new_clip._as = combined

        return new_clip


    def save(self, filename):
        self._as.export(filename)