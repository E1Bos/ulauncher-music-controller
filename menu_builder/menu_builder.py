from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.event import KeywordQueryEvent
from audio_controller import AudioController, PlayerStatus
from event_listeners import Actions


class MenuBuilder:
    """Builds menu items"""

    @staticmethod
    def build_next_track(theme: str) -> ExtensionResultItem:
        """
        Build the next track item

        Args:
            theme (str): The current theme

        Returns:
            ExtensionResultItem: The next track item
        """
        return ExtensionResultItem(
            icon=f"images/{theme}_next.png",
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
        return ExtensionResultItem(
            icon=f"images/{theme}_prev.png",
            name="Previous Track",
            description="Go to the previous song/track",
            on_enter=ExtensionCustomAction(
                {"action": Actions.PREV}, keep_app_open=True
            ),
        )

    @staticmethod
    def build_main_menu(
        theme: str, event: KeywordQueryEvent | None = None
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

        opposite_status: str = (
            PlayerStatus.PAUSED.value
            if AudioController.playing_status() == PlayerStatus.PLAYING
            else PlayerStatus.PLAYING.value
        )

        items.append(
            ExtensionResultItem(
                icon=f"images/{theme}_{opposite_status}.png",
                name=str(opposite_status.capitalize()),
                on_enter=ExtensionCustomAction({"action": Actions.PLAYPAUSE}),
            )
        )

        items.append(MenuBuilder.build_next_track(theme))

        items.append(MenuBuilder.build_previous_track(theme))

        amount: str = event.get_argument() if event else "50"
        items.append(
            ExtensionResultItem(
                icon=f"images/{theme}_volume.png",
                name="Volume",
                description="Set volume between '0-100'",
                on_enter=ExtensionCustomAction(
                    {"action": Actions.SET_VOL, "amount": amount}
                ),
            )
        )

        items.append(
            ExtensionResultItem(
                icon=f"images/{theme}_mute.png",
                name="Mute",
                description="Mute global volume",
                on_enter=ExtensionCustomAction({"action": Actions.MUTE}),
            )
        )

        items.append(
            ExtensionResultItem(
                icon=f"images/{theme}_change_player.png",
                name="Change player",
                description="Change music player",
                on_enter=ExtensionCustomAction(
                    {"action": Actions.PLAYER_SELECT_MENU}, keep_app_open=True
                ),
            )
        )

        return items

    @staticmethod
    def build_player_select(theme) -> list[ExtensionResultItem]:
        """
        Build the player select menu

        Args:
            theme (str): The current theme

        Returns:
            list[ExtensionResultItem]: The player select menu
        """
        players: list[ExtensionResultItem] = []

        for player in AudioController.get_media_players():
            players.append(
                ExtensionResultItem(
                    icon=f"images/{theme}_change_player.png",
                    name=player.split(".")[0].capitalize(),
                    description="Press enter to select this player",
                    on_enter=ExtensionCustomAction(
                        {"action": Actions.SELECT_PLAYER, "player": player}
                    ),
                )
            )
        return players
