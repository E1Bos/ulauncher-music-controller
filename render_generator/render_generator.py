from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.event import KeywordQueryEvent
from audio_controller import AudioController, PlayerStatus
from event_listeners import Actions


class RenderGenerator:
    @staticmethod
    def generate_next(theme: str) -> ExtensionResultItem:
        return ExtensionResultItem(
            icon=f"images/{theme}_next.png",
            name="Next Track",
            description="Go to the next song/track",
            on_enter=ExtensionCustomAction(
                {"action": Actions.NEXT}, keep_app_open=True
            ),
        )

    @staticmethod
    def generate_previous(theme: str) -> ExtensionResultItem:
        return ExtensionResultItem(
            icon=f"images/{theme}_prev.png",
            name="Previous Track",
            description="Go to the previous song/track",
            on_enter=ExtensionCustomAction(
                {"action": Actions.PREV}, keep_app_open=True
            ),
        )

    @staticmethod
    def generate_render(
        theme: str, event: KeywordQueryEvent | None = None
    ) -> list[ExtensionResultItem]:
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

        items.append(RenderGenerator.generate_next(theme))

        items.append(RenderGenerator.generate_previous(theme))

        args = event.get_argument() if event else 50
        items.append(
            ExtensionResultItem(
                icon=f"images/{theme}_volume.png",
                name="Volume",
                description="Set volume between '0-100'",
                on_enter=ExtensionCustomAction(
                    {"action": Actions.SET_VOL, "amount": args}
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

        return items
