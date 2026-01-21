"""Main Textual application for Mofish."""

from pathlib import Path
from typing import Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Footer, Static

from mofish.api import actions
from mofish.api.client import client
from mofish.api.events import parse_message_event
from mofish.config import config
from mofish.state.session import session_state
from mofish.ui.boss_mode import BossMode
from mofish.ui.chatlog import ChatLog
from mofish.ui.input import MessageInput
from mofish.ui.sidebar import SessionItem, Sidebar


class MofishApp(App):
    """Terminal QQ client disguised as developer tools."""

    TITLE = config.window_title
    CSS_PATH = Path(__file__).parent / "ui" / "styles.tcss"

    BINDINGS = [
        Binding("f10", "toggle_boss_mode", "Boss Key", show=False),
        Binding("ctrl+b", "toggle_boss_mode", "Boss Key", show=False),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("escape", "escape_boss_mode", "Exit Boss Mode", show=False),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._boss_mode_active = False
        self._connected = False

    def compose(self) -> ComposeResult:
        # Main layout
        with Container(id="main-container"):
            with Horizontal(id="app-layout"):
                yield Sidebar(id="sidebar")
                with Vertical(id="chat-container"):
                    yield ChatLog(id="chat-log")
                    yield MessageInput(id="message-input")

            # Boss mode overlay (hidden by default)
            yield BossMode(id="boss-mode")

        # Status bar
        yield Static(
            "[#555555]Connecting...[/]",
            id="status-bar",
            markup=True,
        )

    async def on_mount(self) -> None:
        """Initialize on mount."""
        # Hide boss mode initially
        boss_mode = self.query_one("#boss-mode", BossMode)
        boss_mode.display = False

        # Connect to NapCat
        await self._connect()

    async def _connect(self) -> None:
        """Connect to NapCat and load sessions."""
        status = self.query_one("#status-bar", Static)

        # Register event handler
        client.on_event(self._on_event)

        # Connect
        success = await client.connect()
        if not success:
            status.update("[#ff4444]✗ Connection failed[/]")
            return

        self._connected = True
        status.update("[#00ff00]✓ Connected[/]")

        # Load friend and group lists
        await self._load_sessions()

    async def _load_sessions(self) -> None:
        """Load friend and group lists."""
        sidebar = self.query_one("#sidebar", Sidebar)

        # Load friends
        friends = await actions.get_friend_list()
        for friend in friends:
            session_state.add_friend(friend)
            sidebar.add_friend(friend)

        # Load groups
        groups = await actions.get_group_list()
        for group in groups:
            session_state.add_group(group)
            sidebar.add_group(group)

    def _on_event(self, data: dict[str, Any]) -> None:
        """Handle incoming events from NapCat."""
        event = parse_message_event(data)
        if not event:
            return

        # Add message to chat log
        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.add_message(event)

        # Update sidebar preview
        sidebar = self.query_one("#sidebar", Sidebar)
        preview = event.plain_text[:20] or "[媒体消息]"
        sidebar.update_preview(event.session_id, preview)

        # Update session state
        session_state.update_last_message(event.session_id, preview)

        # Increment unread if not active session
        if event.session_id != session_state.active_session_id:
            session_state.increment_unread(event.session_id)
            sidebar.increment_unread(event.session_id)

    def on_session_item_selected(self, message: SessionItem.Selected) -> None:
        """Handle session selection."""
        session_id = message.session_id

        # Update state
        session_state.set_active(session_id)

        # Update UI
        sidebar = self.query_one("#sidebar", Sidebar)
        sidebar.set_active(session_id)
        sidebar.clear_unread(session_id)

        chat_log = self.query_one("#chat-log", ChatLog)
        chat_log.set_session(session_id, message.name)

        # Focus input
        message_input = self.query_one("#message-input", MessageInput)
        message_input.focus_input()

    async def on_message_input_submit(self, message: MessageInput.Submit) -> None:
        """Handle message submission."""
        session = session_state.get_active_session()
        if not session:
            return

        text = message.text

        # Send message
        try:
            if session.is_group:
                await actions.send_group_msg(session.target_id, text)
            else:
                await actions.send_private_msg(session.target_id, text)

            # Add local echo (show our own message)
            from mofish.api.events import create_self_message
            self_msg = create_self_message(text, session.session_id, "我")
            chat_log = self.query_one("#chat-log", ChatLog)
            chat_log.add_message(self_msg)

        except Exception as e:
            status = self.query_one("#status-bar", Static)
            status.update(f"[#ff4444]Send failed: {e}[/]")

    def action_toggle_boss_mode(self) -> None:
        """Toggle boss mode (panic button)."""
        self._boss_mode_active = not self._boss_mode_active

        boss_mode = self.query_one("#boss-mode", BossMode)
        main_container = self.query_one("#main-container", Container)

        if self._boss_mode_active:
            # Show boss mode, hide main content
            boss_mode.is_active = True
            boss_mode.display = True
            main_container.query_one("#app-layout").display = False
        else:
            # Hide boss mode, show main content
            boss_mode.is_active = False
            boss_mode.display = False
            main_container.query_one("#app-layout").display = True

    def action_escape_boss_mode(self) -> None:
        """Exit boss mode if active."""
        if self._boss_mode_active:
            self.action_toggle_boss_mode()
