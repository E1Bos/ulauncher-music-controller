from enum import Enum, auto
import logging
from subprocess import CalledProcessError
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import ItemEnterEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from audio_controller import AudioController

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from main import PlayerMain

logger = logging.getLogger(__name__)


class Actions(Enum):
    PLAYPAUSE = auto()
    NEXT = auto()
    PREV = auto()
    MUTE = auto()
    SET_VOL = auto()
    JUMP = auto()


class InteractionListener(EventListener):
    keep_open_actions = [Actions.NEXT, Actions.PREV]

    def on_event(  # type: ignore
        self, event: ItemEnterEvent, extension: "PlayerMain"
    ) -> None | RenderResultListAction:
        data: dict[str, Any] = event.get_data()
        extension.logger.debug(str(data))

        action = data["action"]

        if action == Actions.PLAYPAUSE:
            AudioController.playpause()
        elif action in [Actions.NEXT, Actions.PREV]:
            try:
                if action == Actions.NEXT:
                    AudioController.next()
                else:
                    AudioController.prev()
                return extension.render_main_page(action)
            except CalledProcessError:
                return extension.render_error(
                    f"Could not play {'next' if action == Actions.NEXT else 'previous'} media",
                    "Does the player support this action?",
                )
        elif action == Actions.MUTE:
            AudioController.global_volume(0)
        elif action == Actions.SET_VOL:
            try:
                query_split: list[str] = data["amount"].split()

                if len(query_split) == 1:
                    raise ValueError("No volume amount provided")

                amount_str: str = "".join(filter(str.isdigit, query_split[1]))

                if not amount_str:
                    raise ValueError(f"{query_split[1]} is not a number")

                amount: int = int(amount_str)
                AudioController.global_volume(amount)
            except (TypeError, ValueError) as e:
                logger.error(
                    f"Could not parse volume amount: {data['amount']}: {e.with_traceback(None)}"
                )

        # elif action == Actions.JUMP:
        #     MusicController.jump(data["pos"])

        # elif action == "show_player":
        #     return extension.render_main_page("change_player")
        # elif action == "change_players":
        #     player_chosen = data["player"]
        #     playerctl.change_player(player_chosen)

        # if action in self.keep_open_actions:
        #     pass
        # return RenderResultListAction()
