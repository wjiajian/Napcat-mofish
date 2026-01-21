"""Handler for incoming OneBot events."""

from typing import TYPE_CHECKING, Any

from textual.app import App

from mofish.api.events import parse_message_event
from mofish.state.session import session_state
from mofish.ui.chatlog import ChatLog
from mofish.ui.sidebar import Sidebar

if TYPE_CHECKING:
    from mofish.app import MofishApp


class EventHandler:
    """Handles incoming OneBot events."""

    def handle_event(self, data: dict[str, Any], app: App) -> None:
        """Handle incoming event data."""
        event = parse_message_event(data)
        if not event:
            return

        try:
            # Add message to talk log
            # Use try-except because UI might not be ready or widget missing
            chat_log = app.query_one("#chat-log", ChatLog)
            chat_log.add_message(event)

            # Update sidebar preview
            sidebar = app.query_one("#sidebar", Sidebar)
            preview = event.plain_text[:20] or "[媒体消息]"
            sidebar.update_preview(event.session_id, preview)

            # Update session state
            session_state.update_last_message(event.session_id, preview)

            # Increment unread if not active session
            if event.session_id != session_state.active_session_id:
                session_state.increment_unread(event.session_id)
                sidebar.increment_unread(event.session_id)

        except Exception:
            pass
