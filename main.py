from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from music_controller import MusicController, PlayerStatus, CurrentSong
from event_listeners import InteractionListener, KeywordListener, Actions
from render_generator import RenderGenerator
from pathlib import Path
import logging
import time

logger = logging.getLogger(__name__)


class PlayerMain(Extension):
    def __init__(self):
        super(PlayerMain, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordListener())
        self.subscribe(ItemEnterEvent, InteractionListener())

    @staticmethod
    def error_item() -> ExtensionResultItem:
        return ExtensionResultItem(
            icon="images/icon.png",
            name="Could not fetch current song",
            description="Is playerctl installed?",
            on_enter=DoNothingAction(),
        )

    @staticmethod
    def no_player_item() -> ExtensionResultItem:
        return ExtensionResultItem(
            icon="images/icon.png",
            name="No Song Playing",
            description="Please start a music player",
            on_enter=DoNothingAction(),
        )

    def get_theme(self) -> str:
        return str(self.preferences["icon_theme"]).lower()

    def render_main_page(self, action: Actions | None = None) -> RenderResultListAction:
        items: list[ExtensionResultItem] = []
        theme: str = self.get_theme()

        current_status: PlayerStatus = MusicController.playing_status()

        if current_status == PlayerStatus.ERROR:
            return RenderResultListAction([PlayerMain.error_item()])

        if current_status == PlayerStatus.NO_PLAYER:
            return RenderResultListAction([PlayerMain.no_player_item()])

        if action is Actions.NEXT:
            items.append(RenderGenerator.generate_next(theme))
            time.sleep(0.1)
        elif action is Actions.PREV:
            items.append(RenderGenerator.generate_previous(theme))
            time.sleep(0.1)

        current_song: CurrentSong = MusicController.get_current_song()
        icon_path: Path = MusicController.download_song_icon(current_song)

        current_song_title = f"{current_song.title}"
        current_song_desc = f"By {current_song.artist} | {current_song.album}"
        items.append(
            ExtensionResultItem(
                icon=str(icon_path),
                name=current_song_title,
                description=current_song_desc,
                on_enter=DoNothingAction(),
            )
        )

        if action is Actions.NEXT or action is Actions.PREV:
            return RenderResultListAction(items)

        items.extend(RenderGenerator.generate_render(theme))

        return RenderResultListAction(items)


if __name__ == "__main__":
    PlayerMain().run()
