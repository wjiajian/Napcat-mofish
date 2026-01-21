"""Sidebar component for session list."""

from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static

from mofish.api.events import FriendInfo, GroupInfo


class SessionItem(Widget):
    """A single session item in the sidebar."""

    DEFAULT_CSS = """
    SessionItem {
        height: 1;
        background: #0d0d0d;
    }
    SessionItem:hover {
        background: #1a1a1a;
    }
    SessionItem:focus {
        background: #1a3319;
    }
    SessionItem.--active {
        background: #1a3319;
    }
    """

    is_active: reactive[bool] = reactive(False)
    unread_count: reactive[int] = reactive(0)

    class Selected(Message):
        """Message sent when session is selected."""

        def __init__(self, session_id: str, name: str) -> None:
            super().__init__()
            self.session_id = session_id
            self.name = name

    def __init__(
        self,
        session_id: str,
        name: str,
        preview: str = "",
        is_group: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.session_id = session_id
        self._name = name
        self._preview = preview
        self._is_group = is_group
        self.can_focus = True

    def compose(self) -> ComposeResult:
        # Compact: just show name, no prefix or preview
        yield Label(self._name[:8], classes="session-name")

    def watch_is_active(self, value: bool) -> None:
        """Update class when active state changes."""
        self.set_class(value, "--active")

    def watch_unread_count(self, value: int) -> None:
        """Update display when unread count changes."""
        # Could add unread badge here
        pass

    def on_click(self) -> None:
        """Handle click event."""
        self.post_message(self.Selected(self.session_id, self._name))

    def update_preview(self, text: str) -> None:
        """Update the preview text."""
        self._preview = text
        try:
            preview_label = self.query_one(".session-preview", Label)
            preview_label.update(text[:20])
        except Exception:
            pass


class Sidebar(Widget):
    """Sidebar containing session list."""

    DEFAULT_CSS = """
    Sidebar {
        width: 10;
        background: #0d0d0d;
        border-right: none;
        padding: 0;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._sessions: dict[str, SessionItem] = {}

    def compose(self) -> ComposeResult:
        # No title, just the list
        yield VerticalScroll(id="session-list")

    def add_friend(self, friend: FriendInfo) -> None:
        """Add a friend to the session list."""
        session_id = friend.session_id
        if session_id not in self._sessions:
            item = SessionItem(
                session_id=session_id,
                name=friend.display_name,
                is_group=False,
                id=f"session-{session_id}",
            )
            self._sessions[session_id] = item
            self.query_one("#session-list", VerticalScroll).mount(item)

    def add_group(self, group: GroupInfo) -> None:
        """Add a group to the session list."""
        session_id = group.session_id
        if session_id not in self._sessions:
            item = SessionItem(
                session_id=session_id,
                name=group.group_name,
                is_group=True,
                id=f"session-{session_id}",
            )
            self._sessions[session_id] = item
            self.query_one("#session-list", VerticalScroll).mount(item)

    def set_active(self, session_id: str) -> None:
        """Set the active session."""
        for sid, item in self._sessions.items():
            item.is_active = (sid == session_id)

    def get_session(self, session_id: str) -> SessionItem | None:
        """Get session item by ID."""
        return self._sessions.get(session_id)

    def update_preview(self, session_id: str, text: str) -> None:
        """Update session preview text."""
        if session_id in self._sessions:
            self._sessions[session_id].update_preview(text)

    def increment_unread(self, session_id: str) -> None:
        """Increment unread count for a session."""
        if session_id in self._sessions:
            self._sessions[session_id].unread_count += 1

    def clear_unread(self, session_id: str) -> None:
        """Clear unread count for a session."""
        if session_id in self._sessions:
            self._sessions[session_id].unread_count = 0
