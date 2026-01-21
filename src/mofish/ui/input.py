"""Input component for message composition with autocomplete support."""

import re
from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Input, Label

from mofish.config import config
from mofish.ui.autocomplete import AutocompletePopup, SLASH_COMMANDS


class MessageInput(Widget):
    """Message input component with terminal-style prompt and autocomplete."""

    DEFAULT_CSS = """
    MessageInput {
        height: auto;
        min-height: 3;
        max-height: 12;
        background: #0d0d0d;
        border-top: solid #1a1a1a;
        padding: 0 1;
    }

    MessageInput > Vertical {
        height: auto;
    }

    MessageInput #input-row {
        height: 3;
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

    MessageInput AutocompletePopup {
        margin-bottom: 1;
    }
    """

    class Submit(Message):
        """Message sent when input is submitted."""

        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    class RequestMentions(Message):
        """Request mention suggestions from app."""

        def __init__(self, query: str) -> None:
            super().__init__()
            self.query = query

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._mention_candidates: list[tuple[str, str]] = []  # (qq, display)
        self._autocomplete_mode: str = ""  # "@", "/", or ""
        self._autocomplete_trigger_pos: int = 0

    def compose(self) -> ComposeResult:
        with Vertical():
            yield AutocompletePopup(id="autocomplete-popup")
            with Horizontal(id="input-row"):
                yield Label(config.prompt_style, id="prompt-label")
                yield Input(placeholder="", id="message-input")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input text changes for autocomplete triggers."""
        text = event.value
        cursor_pos = len(text)  # Approximate cursor position

        # Check for @ trigger - match @ followed by any non-space characters
        at_match = re.search(r"@([^\s]*)$", text)
        if at_match:
            query = at_match.group(1)
            self._autocomplete_mode = "@"
            self._autocomplete_trigger_pos = at_match.start()
            # Request mentions from app
            self.post_message(self.RequestMentions(query))
            return

        # Check for / trigger at start
        if text.startswith("/"):
            self._autocomplete_mode = "/"
            self._autocomplete_trigger_pos = 0
            # Show all commands when just "/" is typed, otherwise filter
            query = text.lower()
            if query == "/":
                # Show all commands
                matches = [(cmd, desc) for cmd, desc in SLASH_COMMANDS]
            else:
                # Filter commands that start with query
                matches = [
                    (cmd, desc) for cmd, desc in SLASH_COMMANDS
                    if cmd.lower().startswith(query)
                ]
            if matches:
                popup = self.query_one("#autocomplete-popup", AutocompletePopup)
                popup.show(matches)
            else:
                self._hide_autocomplete()
            return

        # No trigger, hide autocomplete
        self._hide_autocomplete()

    def _hide_autocomplete(self) -> None:
        """Hide autocomplete popup."""
        self._autocomplete_mode = ""
        try:
            popup = self.query_one("#autocomplete-popup", AutocompletePopup)
            popup.hide()
        except Exception:
            pass

    def show_mentions(self, items: list[tuple[str, str]]) -> None:
        """Show mention suggestions. Called by app with search results."""
        if self._autocomplete_mode != "@":
            return
        try:
            popup = self.query_one("#autocomplete-popup", AutocompletePopup)
            if items:
                popup.show(items)
            else:
                popup.hide()
        except Exception:
            pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission."""
        # First check if autocomplete is active
        try:
            popup = self.query_one("#autocomplete-popup", AutocompletePopup)
            if popup.is_visible:
                if popup.confirm_selection():
                    return
        except Exception:
            pass

        text = event.value.strip()
        if text:
            self.post_message(self.Submit(text))
            event.input.clear()
            self._hide_autocomplete()

    def on_key(self, event) -> None:
        """Handle key events for autocomplete navigation."""
        try:
            popup = self.query_one("#autocomplete-popup", AutocompletePopup)
            if popup.is_visible:
                if event.key == "up":
                    popup.move_selection(-1)
                    event.stop()
                    event.prevent_default()
                elif event.key == "down":
                    popup.move_selection(1)
                    event.stop()
                    event.prevent_default()
                elif event.key == "escape":
                    self._hide_autocomplete()
                    event.stop()
                    event.prevent_default()
                elif event.key == "tab":
                    popup.confirm_selection()
                    event.stop()
                    event.prevent_default()
        except Exception:
            pass

    def on_autocomplete_popup_item_selected(
        self, message: AutocompletePopup.ItemSelected
    ) -> None:
        """Handle autocomplete selection."""
        try:
            input_widget = self.query_one("#message-input", Input)
            current_text = input_widget.value

            if self._autocomplete_mode == "@":
                # Replace @query with @qq
                prefix = current_text[:self._autocomplete_trigger_pos]
                new_text = f"{prefix}@{message.value} "
                input_widget.value = new_text
                input_widget.cursor_position = len(new_text)
            elif self._autocomplete_mode == "/":
                # Replace with command
                input_widget.value = message.value
                input_widget.cursor_position = len(message.value)

            self._autocomplete_mode = ""
        except Exception:
            pass

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

    def append_text(self, text: str) -> None:
        """Append text to input."""
        try:
            input_widget = self.query_one("#message-input", Input)
            current = input_widget.value
            if current and not current.endswith(" "):
                current += " "
            input_widget.value = current + text
            input_widget.cursor_position = len(input_widget.value)
        except Exception:
            pass

    def set_reply(self, message_id: int) -> None:
        """Set up a reply to a message."""
        try:
            input_widget = self.query_one("#message-input", Input)
            input_widget.value = f"/reply {message_id} "
            input_widget.cursor_position = len(input_widget.value)
            input_widget.focus()
        except Exception:
            pass
