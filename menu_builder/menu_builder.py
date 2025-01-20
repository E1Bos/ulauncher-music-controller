import logging
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.event import KeywordQueryEvent
from audio_controller import (
    AudioController,
    MediaPlaybackState,
    PlayerStatus,
    ShuffleState,
    RepeatState,
)
from event_listeners import Actions

logger = logging.getLogger(__name__)


class MenuBuilder:
    """Builds menu items"""

    @staticmethod
    def get_icon_folder(theme: str) -> str:
        return f"images/{theme}"

    @staticmethod
    def build_play_pause(
        theme: str, player_status: PlayerStatus
    ) -> ExtensionResultItem:
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"
        opposite_status: str = (
            MediaPlaybackState.PAUSED.value
            if player_status.playback_state == MediaPlaybackState.PLAYING
            else MediaPlaybackState.PLAYING.value
        )

        return ExtensionResultItem(
            icon=f"{icon_folder}/{opposite_status}.svg",
            name=str(opposite_status.capitalize()),
            description=f"{opposite_status.capitalize()} the current song/track",
            on_enter=ExtensionCustomAction({"action": Actions.PLAYPAUSE}),
        )

    @staticmethod
    def build_next_track(theme: str) -> ExtensionResultItem:
        """
        Build the next track item

        Args:
            theme (str): The current theme

        Returns:
            ExtensionResultItem: The next track item
        """
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"
        return ExtensionResultItem(
            icon=f"{icon_folder}/next.svg",
            name="Next Track",
            description="Go to the next song/track",
            on_enter=ExtensionCustomAction(
                {"action": Actions.NEXT}, keep_app_open=True
            ),
        )

    @staticmethod
    def build_previous_track(theme: str) -> ExtensionResultItem:
        """
        Build the previous track item

        Args:
            theme (str): The current theme

        Returns:
            ExtensionResultItem: The previous track item
        """
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"
        return ExtensionResultItem(
            icon=f"{icon_folder}/prev.svg",
            name="Previous Track",
            description="Go to the previous song/track",
            on_enter=ExtensionCustomAction(
                {"action": Actions.PREV}, keep_app_open=True
            ),
        )

    @staticmethod
    def build_shuffle(
        theme: str, player_status: PlayerStatus
    ) -> ExtensionResultItem | None:
        """Build the shuffle item"""
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"

        if player_status.shuffle_state == ShuffleState.UNAVAILABLE:
            return None
            # return ExtensionResultItem(
            #     icon=f"{icon_folder}/shuffle.svg",
            #     name="Shuffle Unavailable",
            #     description="Current player does not support shuffle",
            #     on_enter=DoNothingAction(),
            # )

        shuffle_str: str = player_status.shuffle_state.name.lower()
        shuffle_opp: str = "off" if shuffle_str == "On" else "on"
        return ExtensionResultItem(
            icon=f"{icon_folder}/shuffle_{shuffle_str}.svg",
            name=f"Shuffle {shuffle_str}",
            description=f"Turn shuffle {shuffle_opp}",
            on_enter=ExtensionCustomAction({"action": Actions.SHUFFLE}),
        )

    @staticmethod
    def build_repeat(
        theme: str, player_status: PlayerStatus
    ) -> ExtensionResultItem | None:
        """Build the repeat item"""

        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"

        if player_status.repeat_state == RepeatState.UNAVAILABLE:
            return None
            # return ExtensionResultItem(
            #     icon=f"{icon_folder}/repeat.svg",
            #     name="Repeat Unavailable",
            #     description="Current player does not support repeating",
            #     on_enter=DoNothingAction(),
            # )

        repeat_str: str = player_status.repeat_state.name.lower()
        repeat_nxt: str = player_status.repeat_state.next().name.lower()
        return ExtensionResultItem(
            icon=f"{icon_folder}/repeat_{repeat_str}.svg",
            name=f"Repeat: {repeat_str.capitalize()}",
            description=f"Switch to {repeat_nxt}",
            on_enter=ExtensionCustomAction(
                {"action": Actions.REPEAT}, keep_app_open=True
            ),
        )

    @staticmethod
    def build_main_menu(
        theme: str,
        event: KeywordQueryEvent | None = None,
        player_status: PlayerStatus | None = None,
    ) -> list[ExtensionResultItem]:
        """
        Build the main user interface, which contains the play/pause,
        next, previous, volume, mute, and change player items

        Args:
            theme (str): The current theme
            event (KeywordQueryEvent | None): The event

        Returns:
            list[ExtensionResultItem]: The main user interface
        """
        items: list[ExtensionResultItem] = []
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"

        player_status = (
            AudioController.get_player_status() if not player_status else player_status
        )

        items.append(MenuBuilder.build_play_pause(theme, player_status))

        items.append(MenuBuilder.build_next_track(theme))

        items.append(MenuBuilder.build_previous_track(theme))

        amount: str = event.get_argument() if event else "50"
        items.append(
            ExtensionResultItem(
                icon=f"{icon_folder}/volume.svg",
                name="Volume",
                description="Set volume between '0-100'",
                on_enter=ExtensionCustomAction(
                    {"action": Actions.SET_VOL, "amount": amount}
                ),
            )
        )

        items.append(
            ExtensionResultItem(
                icon=f"{icon_folder}/mute.svg",
                name="Mute",
                description="Mute global volume",
                on_enter=ExtensionCustomAction({"action": Actions.MUTE}),
            )
        )

        shuffle_item: ExtensionResultItem | None = MenuBuilder.build_shuffle(
            theme, player_status
        )
        if shuffle_item:
            items.append(shuffle_item)

        loop_item: ExtensionResultItem | None = MenuBuilder.build_repeat(
            theme, player_status
        )
        if loop_item:
            items.append(loop_item)

        items.append(
            ExtensionResultItem(
                icon=f"{icon_folder}/switch.svg",
                name="Change player",
                description="Change music player",
                on_enter=ExtensionCustomAction(
                    {"action": Actions.PLAYER_SELECT_MENU}, keep_app_open=True
                ),
            )
        )

        return items

    @staticmethod
    def build_player_select(theme: str) -> list[ExtensionResultItem]:
        """
        Build the player select menu

        Args:
            theme (str): The current theme

        Returns:
            list[ExtensionResultItem]: The player select menu
        """
        players: list[ExtensionResultItem] = []
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"

        for player in AudioController.get_media_players():
            players.append(
                ExtensionResultItem(
                    icon=f"{icon_folder}/switch.svg",
                    name=player.split(".")[0].capitalize(),
                    description="Press enter to select this player",
                    on_enter=ExtensionCustomAction(
                        {"action": Actions.SELECT_PLAYER, "player": player}
                    ),
                )
            )
        return players

    @staticmethod
    def no_media_item(theme: str) -> ExtensionResultItem:
        """
        Build the no media item

        Parameters:
            theme (str): The current theme

        Returns:
            ExtensionResultItem: The no media item
        """
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"
        return ExtensionResultItem(
            icon=f"{icon_folder}/logo.svg",
            name="Could not fetch current media",
            description="Is playerctl installed?",
            on_enter=DoNothingAction(),
        )

    @staticmethod
    def no_player_item(theme: str) -> ExtensionResultItem:
        """
        Build the no player item

        Parameters:
            theme (str): The current theme

        Returns:
            ExtensionResultItem: The no player item
        """
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"
        return ExtensionResultItem(
            icon=f"{icon_folder}/logo.svg",
            name="No Media Playing",
            description="Please start a music player",
            on_enter=HideWindowAction(),
        )

    @staticmethod
    def build_error(theme: str, title: str, message: str) -> ExtensionResultItem:
        """
        Build an error item

        Args:
            theme (str): The current theme
            title (str): The title of the error
            message (str): The error message
        """
        icon_folder: str = f"{MenuBuilder.get_icon_folder(theme)}"
        return ExtensionResultItem(
            icon=f"{icon_folder}/warning.svg",
            name=f"Error: {title}.",
            description=message,
            on_enter=HideWindowAction(),
        )
