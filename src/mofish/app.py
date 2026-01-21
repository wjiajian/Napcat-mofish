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
        
        # Initialize handlers
        from mofish.handlers.event_handler import EventHandler
        from mofish.handlers.input_handler import InputHandler
        from mofish.handlers.mention_handler import MentionHandler
        
        self.input_handler = InputHandler()
        self.mention_handler = MentionHandler()
        self.event_handler = EventHandler()

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
        self.event_handler.handle_event(data, self)

    async def on_session_item_selected(self, message: SessionItem.Selected) -> None:
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

        # Load history
        try:
            is_group = session_id.startswith("group_")
            target_id = int(session_id.split("_")[1])
            
            history = []
            if is_group:
                history = await actions.get_group_msg_history(target_id)
            else:
                history = await actions.get_friend_msg_history(target_id)
            
            # Parse and add messages
            from mofish.api.events import parse_message_event
            
            for msg_data in history:
                # Inject post_type if missing (common in history API)
                if "post_type" not in msg_data:
                    msg_data["post_type"] = "message"
                
                event = parse_message_event(msg_data)
                if event:
                    chat_log.add_message(event)

        except Exception:
            pass

    async def on_message_input_submit(self, message: MessageInput.Submit) -> None:
        """Handle message submission."""
        await self.input_handler.handle_submit(message.text, self)

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

    async def on_message_input_request_mentions(
        self, message: MessageInput.RequestMentions
    ) -> None:
        """Handle @ mention search request."""
        await self.mention_handler.handle_request(message.query, self)

    def on_message_row_clicked(self, message) -> None:
        """Handle message click for reply."""
        from mofish.ui.chatlog import MessageRow

        if hasattr(message, "message_id"):
            message_input = self.query_one("#message-input", MessageInput)
            message_input.set_reply(message.message_id)
