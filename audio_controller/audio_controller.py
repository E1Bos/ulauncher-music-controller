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
    """
    Represents the status of the player
    """

    PLAYING = "play"
    PAUSED = "pause"
    ERROR = auto()
    NO_PLAYER = auto()


@dataclass
class CurrentMedia:
    """
    Represents the current media that is playing
    """

    thumbnail_path: str
    artist: str
    title: str
    album: str | None
    player: str


class AudioController:
    """
    Controller for audio actions
    """

    media_cover_path: Path = Path("/tmp/ulauncher-music-player/media-thumbnails")

    @staticmethod
    def __run_command(command: list[str], check: bool = True) -> str:
        """
        Run a command and return the output
        """
        result = subprocess.run(command, check=check, stdout=subprocess.PIPE, text=True)
        print(result.stdout)
        return result.stdout

    @staticmethod
    def playpause(player: str = "playerctld") -> None:
        """Toggle play/pause"""
        AudioController.__run_command(["playerctl", "--player", player, "play-pause"])

    @staticmethod
    def next(player: str = "playerctld") -> None:
        """Skip to the next track"""
        AudioController.__run_command(["playerctl", "--player", player, "next"])

    @staticmethod
    def prev(player: str = "playerctld") -> None:
        """Skip to the previous track"""
        AudioController.__run_command(["playerctl", "--player", player, "previous"])

    @staticmethod
    def jump(pos: str, player: str = "playerctld") -> None:
        """Jump to a specific position in the track"""
        # TODO: Implement this
        AudioController.__run_command(
            ["playerctl", "--player", player, "position", pos]
        )

    @staticmethod
    def global_volume(set_vol: int) -> None:
        """
        Set the global volume

        Parameters:
            set_vol (int): The volume to set
        """
        cleaned_vol: str = str(max(0, min(set_vol, 100)))
        AudioController.__run_command(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{cleaned_vol}%"]
        )

    @staticmethod
    def shuffle():
        """Toggle shuffle"""
        # TODO: Implement this
        # shuffle = MusicController._run_command(
        #     ["playerctl", "--player", "playerctld", "shuffle"]
        # )
        pass
        # MusicController._run_command(["playerctl", "--player", "playerctld", "shuffle"])

    @staticmethod
    def playing_status(player: str = "playerctld") -> PlayerStatus:
        """
        Get the playing status of the player

        Parameters:
            player (str): The player to check, defaults to "playerctld"

        Returns:
            PlayerStatus: The status of the player
        """
        result = AudioController.__run_command(
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
    def get_media_players() -> list[str]:
        """
        Returns a list of media players that are currently running

        Returns:
            list[str]: A list of media players
        """
        return AudioController.__run_command(["playerctl", "-l"]).splitlines()

    @staticmethod
    def change_player(player: str) -> None:
        """
        Pauses all players and plays the specified player

        Parameters:
            player (str): The player
        """
        AudioController.__run_command(["playerctl", "--all-players", "pause"])
        AudioController.__run_command(["playerctl", "--player", player, "play"])
        AudioController.__run_command(["playerctl", "--player", player, "pause"])
        AudioController.__run_command(["playerctl", "--player", player, "play-pause"])

    @staticmethod
    def get_current_media() -> CurrentMedia:
        """
        Get the current playing media metadata

        Returns:
            CurrentMedia: The current playing media metadata
        """
        result = AudioController.__run_command(
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
            thumbnail_path=artUrl, artist=artist, title=title, album=album, player=player
        )

    @staticmethod
    def __extract_regex_item(
        item: str, search_str: str, ok_if_empty: bool = False
    ) -> str:
        """
        Extract an item from a string using regex, used to extract metadata

        Parameters:
            item (str): The item to extract
            search_str (str): The string to search
            ok_if_empty (bool): Whether to return an empty string if the item is not found

        Returns:
            str: The extracted item string
        """

        match = re.search(rf"{item}:(.+)", search_str)

        if match is None:
            if ok_if_empty:
                return ""

            raise ValueError(f"Could not find {item} in result")

        return match.group(1)

    @staticmethod
    def get_media_thumbnail(media: CurrentMedia) -> Path:
        """
        Get the media thumbnail

        Parameters:
            media (CurrentMedia): The current media

        Returns:
            Path: The path to the media thumbnail
        """
        cover_path: Path = AudioController.media_cover_path

        if not cover_path.exists():
            cover_path.mkdir(parents=True, exist_ok=True)

        local_filename = Path(
            cover_path,
            f"{'-'.join(media.title.split())}-{'-'.join(media.artist.split())}.png",
        )

        if local_filename.exists():
            return local_filename

        old_thumbnails = glob.glob(f"{cover_path}/*.png")
        if len(old_thumbnails) > 50:
            old_thumbnails.sort(key=os.path.getctime)
            for icon in old_thumbnails[:35]:
                os.remove(icon)

        if not os.path.exists(local_filename):
            thumbnail_url: str = media.thumbnail_path

            if thumbnail_url.startswith("file://"):
                local_filename = Path(thumbnail_url[7:])
            elif thumbnail_url.startswith("http"):
                AudioController.__download_thumbnail(media, local_filename)

        return local_filename if local_filename.exists() else Path("images/icon.png")

    @staticmethod
    def __download_thumbnail(media: CurrentMedia, local_filename: Path) -> None:
        """
        Download the thumbnail of the media
        
        Parameters:
            media (CurrentMedia): The current media
            local_filename (Path): The local filename to save the thumbnail
        """
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
                    media.thumbnail_path,
                ],
                check=True,
            )
            if result.returncode != 0:
                os.remove(local_filename)
                logger.error(f"Failed to download image from {media.thumbnail_path}")
        except subprocess.CalledProcessError as e:
            if local_filename.exists():
                os.remove(local_filename)
            logger.error(f"Failed to download image from {media.thumbnail_path}: {e}")
