"""Handler for @ mention search requests."""

from typing import TYPE_CHECKING, Any

from textual.app import App

from mofish.api import actions
from mofish.state.session import session_state
from mofish.ui.input import MessageInput

if TYPE_CHECKING:
    from mofish.app import MofishApp


class MentionHandler:
    """Handles logic for searching and suggesting mentions."""

    def __init__(self) -> None:
        self._group_members_cache: dict[int, list[dict[str, Any]]] = {}

    async def handle_request(self, query: str, app: App) -> None:
        """Handle mention search request."""
        query = query.lower()
        results: list[tuple[str, str]] = []

        # Get current session for group member search
        session = session_state.get_active_session()
        
        if not session:
            return

        if session.is_group:
            group_id = session.target_id
            await self._search_group_members(group_id, query, results)
            # Limit results after search
            results = results[:8]

        # Also add @all option for groups
        if session and session.is_group:
            if "all" in query or not query:
                results.insert(0, ("all", "@全体成员"))

        # Show results
        try:
            message_input = app.query_one("#message-input", MessageInput)
            message_input.show_mentions(results)
        except Exception:
            pass

    async def _search_group_members(
        self, group_id: int, query: str, results: list[tuple[str, str]]
    ) -> None:
        """Search group members and append to results."""
        # Use cached members or fetch
        if group_id not in self._group_members_cache:
            try:
                members = await actions.get_group_member_list(group_id)
                self._group_members_cache[group_id] = members
            except Exception:
                self._group_members_cache[group_id] = []

        members = self._group_members_cache.get(group_id, [])

        # Search group members
        for member in members:
            qq = str(member.get("user_id", ""))
            nickname = member.get("nickname", "")
            card = member.get("card", "")
            display = card or nickname

            # Match by QQ (contains), nickname, or card
            # Empty query matches all
            if not query or (
                query in qq or
                query in nickname.lower() or
                query in card.lower()
            ):
                results.append((qq, f"{display} ({qq})"))

        # Limit results after collecting all matches (in-place modification of results list if I were just appending, but here I can just slice the list before returning?)
        # Actually the method appends to `results`. The caller handles the list.
        # But wait, original code did `results = results[:8]` which is reassignment.
        # Here I passed `results` as argument. I should probably handle the limit in the main method or use strict slicing here.
        # Let's modify logic: filter first then slice in main method.
        pass # The loop above appends all matches. I need to slice it in `handle_request`.
