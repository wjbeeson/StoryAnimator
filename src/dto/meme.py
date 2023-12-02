from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


@dataclass
class BoundingBoxType:
    xmin: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    ymin: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    xmax: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    ymax: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


class CleanMethod(Enum):
    SMART = "SMART"
    SOLID = "SOLID"
    NONE = "NONE"


class ContentType(Enum):
    PICTURE = "Picture"
    CAPTION = "Caption"
    TEXT_BUBBLE = "TextBubble"


@dataclass
class FloatBoundingBoxType:
    xmin: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    ymin: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    xmax: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    ymax: Optional[float] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


class FontSizeNormalizationType(Enum):
    MEAN = "MEAN"
    MIN = "MIN"
    MAX = "MAX"


@dataclass
class FontType:
    color: Optional[str] = field(
        default=None,
        metadata={
            "name": "Color",
            "type": "Attribute",
        }
    )
    highlight_color: Optional[str] = field(
        default=None,
        metadata={
            "name": "HighlightColor",
            "type": "Attribute",
        }
    )
    name: Optional[str] = field(
        default=None,
        metadata={
            "name": "Name",
            "type": "Attribute",
        }
    )
    size: Optional[int] = field(
        default=None,
        metadata={
            "name": "Size",
            "type": "Attribute",
        }
    )
    stroke_color: Optional[str] = field(
        default=None,
        metadata={
            "name": "StrokeColor",
            "type": "Attribute",
        }
    )
    stroke_width: Optional[float] = field(
        default=None,
        metadata={
            "name": "StrokeWidth",
            "type": "Attribute",
        }
    )


class OrientationType(Enum):
    LANDSCAPE = "Landscape"
    PORTRAIT = "Portrait"


@dataclass
class ReactionReferenceType:
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Attribute",
            "required": True,
        }
    )
    o: Optional[float] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )
    f: Optional[bool] = field(
        default=None,
        metadata={
            "type": "Attribute",
        }
    )


class RectifyDurationType(Enum):
    """
    :cvar TRUNCATE: truncate
    :cvar SPEEDUP: speed up or compress
    :cvar FREEZE: freeze
    :cvar REJECT: reject
    :cvar NONE: none
    """
    TRUNCATE = "Truncate"
    SPEEDUP = "Speedup"
    FREEZE = "Freeze"
    REJECT = "Reject"
    NONE = "None"


class SourceType(Enum):
    """
    :cvar TENOR: Tenor gif search
    :cvar VLIPSY: vlipsy movie search
    :cvar LOCAL: Local asset filename.  Can be movie, gif, image (png)
        or audio (wav)
    """
    TENOR = "Tenor"
    VLIPSY = "Vlipsy"
    LOCAL = "Local"


@dataclass
class SpeakType:
    any_element: Optional[object] = field(
        default=None,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
        }
    )


class StateType(Enum):
    CREATED = "CREATED"
    OCR = "OCR"
    OCR_QC = "OCR_QC"
    TTS = "TTS"
    TIMESTAMP = "TIMESTAMP"
    TIMESTAMP_QC = "TIMESTAMP_QC"
    PRODUCED = "PRODUCED"
    PRODUCED_QC = "PRODUCED_QC"


class ZoneType(Enum):
    TITLE = "Title"
    FEATURE = "Feature"
    REACTION = "Reaction"
    CAPTION = "Caption"
    AVATAR = "Avatar"


@dataclass
class ObjectType:
    name: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    pose: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    truncated: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    difficult: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    bndbox: Optional[BoundingBoxType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )


@dataclass
class PictureContent(BoundingBoxType):
    text: Optional["PictureContent.Text"] = field(
        default=None,
        metadata={
            "name": "Text",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    duration: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        }
    )
    background: Optional[str] = field(
        default=None,
        metadata={
            "name": "Background",
            "type": "Attribute",
        }
    )
    clean: Optional[CleanMethod] = field(
        default=None,
        metadata={
            "name": "Clean",
            "type": "Attribute",
            "required": True,
        }
    )
    dont_animate: Optional[bool] = field(
        default=None,
        metadata={
            "name": "DontAnimate",
            "type": "Attribute",
        }
    )
    zoom: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Zoom",
            "type": "Attribute",
        }
    )

    @dataclass
    class Text:
        content: List[object] = field(
            default_factory=list,
            metadata={
                "type": "Wildcard",
                "namespace": "##any",
                "mixed": True,
                "choices": (
                    {
                        "name": "R",
                        "type": ReactionReferenceType,
                        "namespace": "",
                    },
                ),
            }
        )


@dataclass
class ReactionClipType:
    """
    :ivar id:
    :ivar keywords: search keywords or local filename
    :ivar offset: offset from selected playback position.  This amount
        will be added to the timestamp that was selected for clip
        playback.  Specify to obtain precise clip playback time.
    :ivar source: Clip source
    :ivar freeze: Freeze feature while reaction is playing
    :ivar pop_size: Max size of population from which to draw random
        clip.  Specify a smaller number to obtain a higher rank result
    :ivar skip: An optional region to skip from beginning of clip
    :ivar duration: Desired clip duration.  Only meaningful for randomly
        selected clips.  Selected clip will be as close to this value as
        possible, either longer or shorter. Specify -1 to choose a clip
        which fits the available 'display window', which is defined as
        the amount of time before the end of panel, or the next reaction
        clip, whichever is shorter.
    :ivar zone:
    :ivar fullscreen:
    :ivar bounding_box:
    :ivar rectify: Rectify - the action to take if the clip exceeds the
        specified duration
    """
    id: Optional[str] = field(
        default=None,
        metadata={
            "name": "ID",
            "type": "Attribute",
            "required": True,
        }
    )
    keywords: List[str] = field(
        default_factory=list,
        metadata={
            "name": "Keywords",
            "type": "Attribute",
            "required": True,
            "tokens": True,
        }
    )
    offset: Optional[float] = field(
        default=None,
        metadata={
            "name": "Offset",
            "type": "Attribute",
        }
    )
    source: Optional[SourceType] = field(
        default=None,
        metadata={
            "name": "Source",
            "type": "Attribute",
            "required": True,
        }
    )
    freeze: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Freeze",
            "type": "Attribute",
        }
    )
    pop_size: Optional[int] = field(
        default=None,
        metadata={
            "name": "PopSize",
            "type": "Attribute",
        }
    )
    skip: Optional[float] = field(
        default=None,
        metadata={
            "name": "Skip",
            "type": "Attribute",
        }
    )
    duration: Optional[float] = field(
        default=None,
        metadata={
            "name": "Duration",
            "type": "Attribute",
        }
    )
    zone: Optional[ZoneType] = field(
        default=None,
        metadata={
            "name": "Zone",
            "type": "Attribute",
        }
    )
    fullscreen: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Fullscreen",
            "type": "Attribute",
        }
    )
    bounding_box: List[float] = field(
        default_factory=list,
        metadata={
            "name": "BoundingBox",
            "type": "Attribute",
            "tokens": True,
        }
    )
    rectify: Optional[RectifyDurationType] = field(
        default=None,
        metadata={
            "name": "Rectify",
            "type": "Attribute",
        }
    )


@dataclass
class ZoneLayouts:
    zone_layout: List["ZoneLayouts.ZoneLayout"] = field(
        default_factory=list,
        metadata={
            "name": "ZoneLayout",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        }
    )

    @dataclass
    class ZoneLayout:
        zone: List["ZoneLayouts.ZoneLayout.Zone"] = field(
            default_factory=list,
            metadata={
                "name": "Zone",
                "type": "Element",
                "namespace": "",
                "min_occurs": 1,
            }
        )
        name: Optional[str] = field(
            default=None,
            metadata={
                "name": "Name",
                "type": "Attribute",
                "required": True,
            }
        )
        orientation: Optional[OrientationType] = field(
            default=None,
            metadata={
                "name": "Orientation",
                "type": "Attribute",
                "required": True,
            }
        )

        @dataclass
        class Zone:
            bounding_box: List[FloatBoundingBoxType] = field(
                default_factory=list,
                metadata={
                    "name": "BoundingBox",
                    "type": "Element",
                    "namespace": "",
                    "min_occurs": 1,
                }
            )
            type: Optional[ZoneType] = field(
                default=None,
                metadata={
                    "name": "Type",
                    "type": "Attribute",
                    "required": True,
                }
            )


@dataclass
class CaptionContent(PictureContent):
    speak: Optional[SpeakType] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
        }
    )
    timestamps: List[float] = field(
        default_factory=list,
        metadata={
            "name": "Timestamps",
            "type": "Element",
            "namespace": "",
            "required": True,
            "tokens": True,
        }
    )
    ocr: Optional[bool] = field(
        default=None,
        metadata={
            "name": "OCR",
            "type": "Attribute",
            "required": True,
        }
    )


@dataclass
class Annotation:
    class Meta:
        name = "annotation"

    folder: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    filename: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    path: Optional[str] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    source: Optional["Annotation.Source"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    size: Optional["Annotation.Size"] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    segmented: Optional[int] = field(
        default=None,
        metadata={
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    object_value: List[ObjectType] = field(
        default_factory=list,
        metadata={
            "name": "object",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        }
    )

    @dataclass
    class Source:
        database: Optional[str] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "",
                "required": True,
            }
        )

    @dataclass
    class Size:
        width: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "",
                "required": True,
            }
        )
        height: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "",
                "required": True,
            }
        )
        depth: Optional[int] = field(
            default=None,
            metadata={
                "type": "Element",
                "namespace": "",
                "required": True,
            }
        )


@dataclass
class TextBubbleContent(CaptionContent):
    font: Optional[FontType] = field(
        default=None,
        metadata={
            "name": "Font",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    group: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Group",
            "type": "Attribute",
        }
    )


@dataclass
class PanelType(BoundingBoxType):
    content: List["PanelType.Content"] = field(
        default_factory=list,
        metadata={
            "name": "Content",
            "type": "Element",
            "namespace": "",
        }
    )
    comment: Optional[bool] = field(
        default=None,
        metadata={
            "name": "Comment",
            "type": "Attribute",
        }
    )

    @dataclass
    class Content:
        text_bubble: Optional[TextBubbleContent] = field(
            default=None,
            metadata={
                "name": "TextBubble",
                "type": "Element",
                "namespace": "",
            }
        )
        caption: Optional[CaptionContent] = field(
            default=None,
            metadata={
                "name": "Caption",
                "type": "Element",
                "namespace": "",
            }
        )
        picture: Optional[PictureContent] = field(
            default=None,
            metadata={
                "name": "Picture",
                "type": "Element",
                "namespace": "",
            }
        )
        type: Optional[ContentType] = field(
            default=None,
            metadata={
                "name": "Type",
                "type": "Attribute",
            }
        )
        speaker: Optional[int] = field(
            default=None,
            metadata={
                "name": "Speaker",
                "type": "Attribute",
            }
        )


@dataclass
class Meme:
    header: Optional["Meme.Header"] = field(
        default=None,
        metadata={
            "name": "Header",
            "type": "Element",
            "namespace": "",
            "required": True,
        }
    )
    reactions: List[ReactionClipType] = field(
        default_factory=list,
        metadata={
            "name": "Reactions",
            "type": "Element",
            "namespace": "",
        }
    )
    panels: List[PanelType] = field(
        default_factory=list,
        metadata={
            "name": "Panels",
            "type": "Element",
            "namespace": "",
            "min_occurs": 1,
        }
    )
    sequential: Optional["Meme.Sequential"] = field(
        default=None,
        metadata={
            "name": "Sequential",
            "type": "Element",
            "namespace": "",
        }
    )

    @dataclass
    class Header:
        state: Optional[StateType] = field(
            default=None,
            metadata={
                "name": "State",
                "type": "Element",
                "namespace": "",
                "required": True,
            }
        )
        speakers: Optional["Meme.Header.Speakers"] = field(
            default=None,
            metadata={
                "name": "Speakers",
                "type": "Element",
                "namespace": "",
                "required": True,
            }
        )
        font_size_normalization: Optional[FontSizeNormalizationType] = field(
            default=None,
            metadata={
                "name": "FontSizeNormalization",
                "type": "Attribute",
            }
        )

        @dataclass
        class Speakers:
            speaker: List["Meme.Header.Speakers.Speaker"] = field(
                default_factory=list,
                metadata={
                    "name": "Speaker",
                    "type": "Element",
                    "namespace": "",
                    "min_occurs": 1,
                }
            )

            @dataclass
            class Speaker:
                text_properties: Optional[FontType] = field(
                    default=None,
                    metadata={
                        "name": "TextProperties",
                        "type": "Element",
                        "namespace": "",
                        "required": True,
                    }
                )
                avatar_filename: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "AvatarFilename",
                        "type": "Element",
                        "namespace": "",
                        "required": True,
                    }
                )
                voice: Optional[str] = field(
                    default=None,
                    metadata={
                        "name": "Voice",
                        "type": "Attribute",
                        "required": True,
                    }
                )
                speed: Optional[float] = field(
                    default=None,
                    metadata={
                        "name": "Speed",
                        "type": "Attribute",
                    }
                )

    @dataclass
    class Sequential:
        margin: Optional[int] = field(
            default=None,
            metadata={
                "name": "Margin",
                "type": "Attribute",
            }
        )
        preferred_axis: Optional[OrientationType] = field(
            default=None,
            metadata={
                "name": "PreferredAxis",
                "type": "Attribute",
            }
        )
        crawl_speed: Optional[float] = field(
            default=None,
            metadata={
                "name": "CrawlSpeed",
                "type": "Attribute",
            }
        )
