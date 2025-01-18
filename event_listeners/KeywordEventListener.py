import logging
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from render_generator import RenderGenerator

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import PlayerMain

logger = logging.getLogger(__name__)


class KeywordListener(EventListener):
    def on_event(  # type: ignore
        self, event: KeywordQueryEvent, extension: "PlayerMain"
    ) -> RenderResultListAction:
        theme = extension.get_theme()
        query: str = event.get_argument()

        if query is None:
            return extension.render_main_page()

        render_items = RenderGenerator.generate_render(theme, event)

        search_terms: list[str] = query.lower().split()
        matched_search = [
            item
            for item in render_items
            if any(term in item.get_name().lower() for term in search_terms)
        ]

        return RenderResultListAction(matched_search)
