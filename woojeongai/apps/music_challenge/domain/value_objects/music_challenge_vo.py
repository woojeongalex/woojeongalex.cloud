from enum import Enum


class ChallengeType(str, Enum):
    VOCAL = "vocal"
    INSTRUMENT = "instrument"
    BOTH = "both"


class MediaType(str, Enum):
    AUDIO = "audio"
    VIDEO = "video"
