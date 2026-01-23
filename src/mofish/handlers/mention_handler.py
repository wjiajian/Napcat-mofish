"""Handler for @ mention search requests."""

from typing import TYPE_CHECKING

from textual.app import App

from mofish.state.member_cache import member_cache
from mofish.state.session import session_state
from mofish.ui.input import MessageInput

if TYPE_CHECKING:
    from mofish.app import MofishApp


class MentionHandler:
    """Handles logic for searching and suggesting mentions."""

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
        # 使用共享的 member_cache 服务喵～
        await member_cache.ensure_cache(group_id)
        members = member_cache.get_members_list(group_id)

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

