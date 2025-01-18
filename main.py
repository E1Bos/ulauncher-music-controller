from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from audio_controller import AudioController, PlayerStatus, CurrentMedia
from event_listeners import InteractionListener, KeywordListener, Actions
from menu_builder import MenuBuilder
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
    def no_media_item() -> ExtensionResultItem:
        return ExtensionResultItem(
            icon="images/icon.png",
            name="Could not fetch current media",
            description="Is playerctl installed?",
            on_enter=DoNothingAction(),
        )

    @staticmethod
    def no_player_item() -> ExtensionResultItem:
        return ExtensionResultItem(
            icon="images/icon.png",
            name="No Media Playing",
            description="Please start a music player",
            on_enter=DoNothingAction(),
        )

    def render_error(self, title: str, message: str) -> RenderResultListAction:
        theme: str = self.get_theme()
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon=f"images/{theme}_error.png",
                    name=f"Error: {title}",
                    description=message,
                    on_enter=HideWindowAction(),
                )
            ]
        )

    def get_theme(self) -> str:
        return str(self.preferences["icon_theme"]).lower()

    def render_main_page(self, action: Actions | None = None) -> RenderResultListAction:
        logger.info(f"Current directory: {Path.cwd()}")
        theme: str = self.get_theme()
        items: list[ExtensionResultItem] = []

        current_status: PlayerStatus = AudioController.playing_status()

        if current_status == PlayerStatus.ERROR:
            return RenderResultListAction([PlayerMain.no_media_item()])

        if current_status == PlayerStatus.NO_PLAYER:
            return RenderResultListAction([PlayerMain.no_player_item()])

        if action is Actions.NEXT:
            items.append(MenuBuilder.build_next_track(theme))
            time.sleep(0.1)
        elif action is Actions.PREV:
            items.append(MenuBuilder.build_previous_track(theme))
            time.sleep(0.1)

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

        if action is Actions.NEXT or action is Actions.PREV:
            return RenderResultListAction(items)

        items.extend(MenuBuilder.build_main_menu(theme))

        return RenderResultListAction(items)

    def render_players(self) -> RenderResultListAction:
        theme: str = self.get_theme()

        items = MenuBuilder.build_player_select(theme)

        return RenderResultListAction(items)


if __name__ == "__main__":
    PlayerMain().run()
