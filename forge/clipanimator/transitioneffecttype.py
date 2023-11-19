from enum import Enum
class TransitionEffectType(Enum):
    NONE=0
    POP = 1
    POP_LEFT = 3
    POP_RIGHT = 5
    FADE = 8
