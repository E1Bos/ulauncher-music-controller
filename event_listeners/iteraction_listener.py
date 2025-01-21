from enum import Enum, auto
import logging
import time
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


class InteractionListener(EventListener):
    """Listener for user interactions"""

    "Max wait time for media change in seconds"
    MAX_WAIT: int = 3

    @staticmethod
    def under_max_wait(start_time: float) -> bool:
        return (time.time() - start_time) < InteractionListener.MAX_WAIT

    def on_event(  # type: ignore
        self, event: ItemEnterEvent, extension: "PlayerMain"
    ) -> None | RenderResultListAction:
        """
        Handle user interactions

        Parameters:
            event (ItemEnterEvent): The event that was triggered
            extension (PlayerMain): The main extension class

        Returns:
            None | RenderResultListAction: Nothing or a list of items to render
        """
        data: dict[str, Any] = event.get_data()
        extension.logger.debug(str(data))

        action: Actions = data["action"]
        components: list[str] = data.get("components", [])
        player_status = AudioController.get_player_status()

        start_time = time.time()
        previous_media = AudioController.get_current_media()

        if action == Actions.PLAYPAUSE:
            AudioController.playpause()
        elif action in [Actions.NEXT, Actions.PREV]:
            try:
                if action == Actions.NEXT:
                    AudioController.next()
                else:
                    AudioController.prev()

                current_media = AudioController.get_current_media()
                if action == Actions.NEXT:
                    while InteractionListener.under_max_wait(start_time):
                        current_media = AudioController.get_current_media()

                        if current_media.title != previous_media.title:
                            break

                        time.sleep(0.1)
                elif action == Actions.PREV:
                    while InteractionListener.under_max_wait(start_time):
                        current_media = AudioController.get_current_media()

                        if current_media.title != previous_media.title:
                            break

                        new_pos = current_media.position
                        old_pos = previous_media.position

                        if new_pos is not None and old_pos is not None:
                            if new_pos < old_pos:
                                break

                        time.sleep(0.1)

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
                if len(components) == 0:
                    raise ValueError("No volume amount provided")

                vol_component: str = components[0]
                vol_amount_str: str = "".join(filter(str.isdigit, vol_component))

                if not vol_amount_str:
                    raise ValueError(f"{vol_component} is not a number")

                vol_int: int = int(vol_amount_str)
                AudioController.global_volume(vol_int)
            except (TypeError, ValueError) as e:
                logger.error(
                    f"Could not parse volume amount: {data['amount']}: {e.with_traceback(None)}"
                )
        elif action == Actions.SHUFFLE:
            AudioController.shuffle()
        elif action == Actions.REPEAT:
            start_time = time.time()
            AudioController.repeat(player_status)

            while InteractionListener.under_max_wait(start_time):
                new_status = AudioController.get_player_status()
                if new_status.repeat_state != player_status.repeat_state:
                    break

                time.sleep(0.1)

            return extension.render_main_page(action)
        elif action == Actions.PLAYER_SELECT_MENU:
            return extension.render_players()
        elif action == Actions.SELECT_PLAYER:
            AudioController.change_player(data["player"])
