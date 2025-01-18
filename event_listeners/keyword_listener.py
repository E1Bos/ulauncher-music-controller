import logging
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from menu_builder import MenuBuilder

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PlayerMain

logger = logging.getLogger(__name__)


class KeywordListener(EventListener):
    """Listener for keyword queries"""

    def on_event(  # type: ignore
        self, event: KeywordQueryEvent, extension: "PlayerMain"
    ) -> RenderResultListAction:
        """
        Render the main page or search for a query

        Parameters:
            event (KeywordQueryEvent): The event that was triggered
            extension (PlayerMain): The main extension class

        Returns:
            RenderResultListAction: A list of items to render
        """
        theme: str = extension.get_theme()
        query: str = event.get_argument()

        if query is None:
            return extension.render_main_page()

        render_items: list[ExtensionResultItem] = MenuBuilder.build_main_menu(
            theme, event
        )

        search_terms: list[str] = query.lower().split()
        matched_search: list[ExtensionResultItem] = [
            item
            for item in render_items
            if any(term in item.get_name().lower() for term in search_terms)
        ]

        return RenderResultListAction(matched_search)
