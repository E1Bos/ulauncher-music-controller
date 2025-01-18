from dataclasses import dataclass
from enum import Enum, auto
import glob
import os
from pathlib import Path
import subprocess
import logging
import re

logger = logging.getLogger(__name__)


class PlayerStatus(Enum):
    PLAYING = "play"
    PAUSED = "pause"
    ERROR = auto()
    NO_PLAYER = auto()


@dataclass
class CurrentMedia:
    icon: str
    artist: str
    title: str
    album: str | None
    player: str


class AudioController:
    media_cover_path: Path = Path("/tmp/ulauncher-music-player/media-thumbnails")

    @staticmethod
    def _run_command(command: list[str], check: bool = True) -> str:
        result = subprocess.run(command, check=check, stdout=subprocess.PIPE, text=True)
        print(result.stdout)
        return result.stdout

    @staticmethod
    def playpause(player: str = "playerctld") -> None:
        AudioController._run_command(["playerctl", "--player", player, "play-pause"])

    @staticmethod
    def next(player: str = "playerctld") -> None:
        AudioController._run_command(["playerctl", "--player", player, "next"])

    @staticmethod
    def prev(player: str = "playerctld") -> None:
        AudioController._run_command(["playerctl", "--player", player, "previous"])

    @staticmethod
    def jump(pos: str, player: str = "playerctld") -> None:
        AudioController._run_command(["playerctl", "--player", player, "position", pos])

    @staticmethod
    def global_volume(set_vol: int) -> None:
        cleaned_vol: str = str(max(0, min(set_vol, 100)))
        AudioController._run_command(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{cleaned_vol}%"]
        )

    @staticmethod
    def shuffle():
        # shuffle = MusicController._run_command(
        #     ["playerctl", "--player", "playerctld", "shuffle"]
        # )
        pass
        # MusicController._run_command(["playerctl", "--player", "playerctld", "shuffle"])

    @staticmethod
    def playing_status(player: str = "playerctld") -> PlayerStatus:
        result = AudioController._run_command(
            ["playerctl", "--player", player, "status"], False
        )

        if "No player found" in result:
            return PlayerStatus.NO_PLAYER

        if "Playing" in result:
            return PlayerStatus.PLAYING

        if "Paused" in result:
            return PlayerStatus.PAUSED

        return PlayerStatus.ERROR

    @staticmethod
    def get_current_media() -> CurrentMedia:
        result = AudioController._run_command(
            [
                "playerctl",
                "metadata",
                "--format",
                "artUrl:{{mpris:artUrl}}\nartist:{{xesam:artist}}\ntitle:{{xesam:title}}\nalbum:{{xesam:album}}\nplayerName:{{playerName}}",
            ]
        )

        artUrl = AudioController.__extract_regex_item("artUrl", result)
        artist = AudioController.__extract_regex_item("artist", result)
        title = AudioController.__extract_regex_item("title", result)
        album = AudioController.__extract_regex_item("album", result, ok_if_empty=True)
        player = AudioController.__extract_regex_item("playerName", result).capitalize()

        return CurrentMedia(
            icon=artUrl, artist=artist, title=title, album=album, player=player
        )

    @staticmethod
    def __extract_regex_item(item: str, result: str, ok_if_empty: bool = False) -> str:
        match = re.search(rf"{item}:(.+)", result)

        if match is None:
            if ok_if_empty:
                return ""

            raise ValueError(f"Could not find {item} in result")

        return match.group(1)

    @staticmethod
    def get_media_icon(media: CurrentMedia) -> Path:
        cover_path: Path = AudioController.media_cover_path

        if not cover_path.exists():
            cover_path.mkdir(parents=True, exist_ok=True)

        local_filename = Path(
            cover_path,
            f"{'-'.join(media.title.split())}-{'-'.join(media.artist.split())}.png",
        )

        if local_filename.exists():
            return local_filename

        old_icons = glob.glob(f"{cover_path}/*.png")
        if len(old_icons) > 50:
            old_icons.sort(key=os.path.getctime)
            for icon in old_icons[:35]:
                os.remove(icon)

        if not os.path.exists(local_filename):
            icon_url: str = media.icon

            if icon_url.startswith("file://"):
                local_filename = Path(icon_url[7:])
            elif icon_url.startswith("http"):
                AudioController._download_icon(media, local_filename)

        return local_filename if local_filename.exists() else Path("images/icon.png")

    @staticmethod
    def _download_icon(media: CurrentMedia, local_filename: Path) -> None:
        try:
            result = subprocess.run(
                [
                    "wget",
                    "-t",
                    "1",
                    "-T",
                    "0.3",
                    "-O",
                    str(local_filename),
                    media.icon,
                ],
                check=True,
            )
            if result.returncode != 0:
                os.remove(local_filename)
                logger.error(f"Failed to download image from {media.icon}")
        except subprocess.CalledProcessError as e:
            if local_filename.exists():
                os.remove(local_filename)
            logger.error(f"Failed to download image from {media.icon}: {e}")
