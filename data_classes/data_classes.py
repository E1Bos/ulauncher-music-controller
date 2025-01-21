from dataclasses import dataclass
from enum import Enum, auto


class MediaPlaybackState(Enum):
    """Represents the status of the player"""

    PLAYING = "play"
    PAUSED = "pause"
    ERROR = auto()
    NO_PLAYER = auto()


class ShuffleState(Enum):
    """Represents the shuffle status of the player"""

    ON = "On"
    OFF = "Off"
    UNAVAILABLE = auto()


class RepeatState(Enum):
    """Represents the loop of the player"""

    OFF = "None"
    PLAYLIST = "Playlist"
    TRACK = "Track"
    UNAVAILABLE = "Unavailable"

    def next(self) -> "RepeatState":
        order = [RepeatState.OFF, RepeatState.PLAYLIST, RepeatState.TRACK]

        if self == RepeatState.UNAVAILABLE:
            return RepeatState.UNAVAILABLE

        return order[(order.index(self) + 1) % len(order)]


class Actions(Enum):
    """Actions that can be performed"""

    PLAYPAUSE = auto()
    NEXT = auto()
    PREV = auto()
    MUTE = auto()
    SHUFFLE = auto()
    REPEAT = auto()
    SET_VOL = auto()
    JUMP = auto()
    PLAYER_SELECT_MENU = auto()
    SELECT_PLAYER = auto()


@dataclass
class PlayerStatus:
    """Represents the status of the player"""

    playback_state: MediaPlaybackState
    shuffle_state: ShuffleState
    repeat_state: RepeatState


@dataclass
class CurrentMedia:
    """Represents the current media that is playing"""

    thumbnail_path: str
    artist: str
    title: str
    player: str
    album: str | None
    position: int | None


@dataclass
class Query:
    command: str
    components: list[str]
