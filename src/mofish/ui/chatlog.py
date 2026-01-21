"""Chat log component for displaying messages."""

from datetime import datetime

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from mofish.api.events import MessageEvent
from mofish.config import config


class MessageRow(Static):
    """A single message in the chat log."""

    DEFAULT_CSS = """
    MessageRow {
        height: auto;
        margin: 0;
    }
    MessageRow:hover {
        background: #1a1a1a;
    }
    """

    class Clicked(Message):
        """Sent when message is clicked for reply."""

        def __init__(self, message_id: int) -> None:
            super().__init__()
            self.message_id = message_id

    def __init__(self, event: MessageEvent, is_highlight: bool = False) -> None:
        self._message_id = event.message_id

        # Format time
        time_str = datetime.fromtimestamp(event.time).strftime("%H:%M:%S")

        # Format content
        content = self._format_content(event)

        # Build display
        sender_style = "[#00aa00 bold]"
        time_style = "[#444444]"

        if is_highlight:
            content_style = "[#ffff00 bold]"
        else:
            content_style = "[#888888]"

        text = (
            f"{time_style}{time_str}[/] "
            f"{sender_style}{event.display_name}[/]: "
            f"{content_style}{content}[/]"
        )

        super().__init__(text, markup=True)

    def _format_content(self, event: MessageEvent) -> str:
        """Format message content, replacing images with placeholders."""
        parts: list[str] = []
        for seg in event.segments:
            if seg.type == "text":
                parts.append(seg.text)
            elif seg.type == "image":
                parts.append("[图片]")
            elif seg.type == "face":
                parts.append("[表情]")
            elif seg.type == "at":
                qq = seg.at_qq
                parts.append(f"@{qq}")
            else:
                parts.append(f"[{seg.type}]")
        return "".join(parts) or "[空消息]"

    def on_click(self) -> None:
        """Handle click to reply."""
        if self._message_id:
            self.post_message(self.Clicked(self._message_id))


class ChatLog(Widget):
    """Chat log container."""

    DEFAULT_CSS = """
    ChatLog {
        background: #0a0a0a;
        padding: 0 1;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._session_id: str = ""
        self._messages: dict[str, list[MessageEvent]] = {}

    def compose(self) -> ComposeResult:
        yield Static("[Chat Log]", id="chat-header-title")
        yield VerticalScroll(id="message-scroll")

    def set_session(self, session_id: str, name: str) -> None:
        """Switch to a different session."""
        self._session_id = session_id

        # Update header
        try:
            header = self.query_one("#chat-header-title", Static)
            header.update(f"[{name}]")
        except Exception:
            pass

        # Re-render messages
        self._render_messages()

    def add_message(self, event: MessageEvent) -> None:
        """Add a message to the log."""
        session_id = event.session_id

        if session_id not in self._messages:
            self._messages[session_id] = []

        self._messages[session_id].append(event)

        # Trim buffer
        if len(self._messages[session_id]) > config.message_buffer_size:
            self._messages[session_id] = self._messages[session_id][-config.message_buffer_size:]

        # If this is current session, add to view
        if session_id == self._session_id:
            is_highlight = self._should_highlight(event)
            try:
                scroll = self.query_one("#message-scroll", VerticalScroll)
                row = MessageRow(event, is_highlight=is_highlight)
                scroll.mount(row)
                scroll.scroll_end(animate=False)
            except Exception:
                pass

    def _render_messages(self) -> None:
        """Render all messages for current session."""
        try:
            scroll = self.query_one("#message-scroll", VerticalScroll)
            scroll.remove_children()

            messages = self._messages.get(self._session_id, [])
            for event in messages:
                is_highlight = self._should_highlight(event)
                scroll.mount(MessageRow(event, is_highlight=is_highlight))

            scroll.scroll_end(animate=False)
        except Exception:
            pass

    def _should_highlight(self, event: MessageEvent) -> bool:
        """Check if message should be highlighted."""
        text = event.plain_text.lower()

        # Check keywords
        for keyword in config.highlight_keywords:
            if keyword.lower() in text:
                return True

        # Check if mentioned
        if config.my_name and config.my_name.lower() in text:
            return True

        return False

    def clear(self) -> None:
        """Clear current session messages from view."""
        try:
            scroll = self.query_one("#message-scroll", VerticalScroll)
            scroll.remove_children()
        except Exception:
            pass
