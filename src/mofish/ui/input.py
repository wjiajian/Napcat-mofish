"""Input component for message composition."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label

from mofish.config import config


class MessageInput(Widget):
    """Message input component with terminal-style prompt."""

    DEFAULT_CSS = """
    MessageInput {
        height: 3;
        background: #0d0d0d;
        border-top: solid #1a1a1a;
        padding: 0 1;
    }

    MessageInput > Horizontal {
        height: 100%;
        align: left middle;
    }

    MessageInput #prompt-label {
        color: #00ff00;
        width: auto;
        padding: 0 1 0 0;
    }

    MessageInput #message-input {
        background: #0a0a0a;
        color: #00cc00;
        border: none;
        width: 1fr;
    }

    MessageInput #message-input:focus {
        border: none;
    }
    """

    class Submit(Message):
        """Message sent when input is submitted."""

        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(config.prompt_style, id="prompt-label")
            yield Input(placeholder="", id="message-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        text = event.value.strip()
        if text:
            self.post_message(self.Submit(text))
            event.input.clear()

    def focus_input(self) -> None:
        """Focus the input field."""
        try:
            self.query_one("#message-input", Input).focus()
        except Exception:
            pass

    def clear(self) -> None:
        """Clear the input field."""
        try:
            self.query_one("#message-input", Input).clear()
        except Exception:
            pass
