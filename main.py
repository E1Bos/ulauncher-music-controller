from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from audio_controller import (
    AudioController,
    CurrentMedia,
    PlayerStatus,
    MediaPlaybackState,
)
from event_listeners import InteractionListener, KeywordListener, Actions
from menu_builder import MenuBuilder
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PlayerMain(Extension):
    __keep_open: list[Actions] = [Actions.NEXT, Actions.PREV, Actions.REPEAT]
    __aliases = {
        "n": "next",
        "b": "previous",
        "m": "mute",
        "v": "volume",
        "r": "repeat",
        "s": "shuffle",
    }

    def __init__(self):
        super(PlayerMain, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordListener())
        self.subscribe(ItemEnterEvent, InteractionListener())

    def get_aliases(self) -> dict[str, str]:
        player_status = AudioController.get_player_status()
        aliases = {
            "p": "play"
            if player_status.playback_state == MediaPlaybackState.PAUSED
            else "pause",
        }

        aliases.update(self.__aliases)

        return aliases

    def get_theme(self) -> str:
        return str(self.preferences["icon_theme"]).lower()

    def render_error(self, title: str, message: str) -> RenderResultListAction:
        return RenderResultListAction(
            [MenuBuilder.build_error(self.get_theme(), title, message)]
        )

    def render_main_page(self, action: Actions | None = None) -> RenderResultListAction:
        logger.info(f"Current directory: {Path.cwd()}")
        theme: str = self.get_theme()
        items: list[ExtensionResultItem] = []

        player_status: PlayerStatus = AudioController.get_player_status()

        playback_state: MediaPlaybackState = player_status.playback_state
        logger.debug(f"Current status: {player_status}")

        if playback_state == MediaPlaybackState.ERROR:
            return RenderResultListAction([MenuBuilder.no_media_item(theme)])

        if playback_state == MediaPlaybackState.NO_PLAYER:
            return RenderResultListAction([MenuBuilder.no_player_item(theme)])

        if action is Actions.NEXT:
            items.append(MenuBuilder.build_next_track(theme))
        elif action is Actions.PREV:
            items.append(MenuBuilder.build_previous_track(theme))
        elif action is Actions.REPEAT:
            repeat_item = MenuBuilder.build_repeat(theme, player_status)

            if repeat_item:
                items.append(repeat_item)

        current_media: CurrentMedia = AudioController.get_current_media()
        icon_path: Path = AudioController.get_media_thumbnail(current_media)

        current_media_title = f"{current_media.title}"
        album = f" | {current_media.album}" if current_media.album else ""
        current_media_desc = (
            f"By {current_media.artist}{album} | {current_media.player}"
        )
        items.append(
            ExtensionResultItem(
                icon=str(icon_path),
                name=current_media_title,
                description=current_media_desc,
                on_enter=DoNothingAction(),
            )
        )

        if action in self.__keep_open:
            return RenderResultListAction(items)

        items.extend(MenuBuilder.build_main_menu(theme=theme, player_status=player_status))

        return RenderResultListAction(items)

    def render_players(self) -> RenderResultListAction:
        theme: str = self.get_theme()

        items = MenuBuilder.build_player_select(theme)

        return RenderResultListAction(items)


if __name__ == "__main__":
    PlayerMain().run()
