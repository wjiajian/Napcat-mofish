"""Autocomplete popup component for @ mentions and commands."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label, Static


class AutocompleteItem(Static):
    """Single autocomplete suggestion item."""

    DEFAULT_CSS = """
    AutocompleteItem {
        height: 1;
        padding: 0 1;
        background: #1a1a1a;
        color: #00cc00;
    }
    AutocompleteItem:hover {
        background: #2a2a2a;
    }
    AutocompleteItem.--selected {
        background: #1a3319;
        color: #00ff00;
    }
    """

    is_selected: reactive[bool] = reactive(False)

    class Selected(Message):
        """Sent when item is selected."""

        def __init__(self, value: str, display: str) -> None:
            super().__init__()
            self.value = value
            self.display = display

    def __init__(self, value: str, display: str, **kwargs) -> None:
        super().__init__(display, **kwargs)
        self._value = value
        self._display = display

    def watch_is_selected(self, value: bool) -> None:
        self.set_class(value, "--selected")

    def on_click(self) -> None:
        self.post_message(self.Selected(self._value, self._display))


class AutocompletePopup(Widget):
    """Popup showing autocomplete suggestions."""

    DEFAULT_CSS = """
    AutocompletePopup {
        height: auto;
        max-height: 8;
        background: #0d0d0d;
        border: solid #333333;
        display: none;
    }
    AutocompletePopup.--visible {
        display: block;
    }
    """

    is_visible: reactive[bool] = reactive(False)

    class ItemSelected(Message):
        """Sent when an item is selected from popup."""

        def __init__(self, value: str, display: str) -> None:
            super().__init__()
            self.value = value
            self.display = display

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._items: list[tuple[str, str]] = []  # (value, display)
        self._selected_index = 0

    def compose(self) -> ComposeResult:
        yield Vertical(id="autocomplete-list")

    def show(self, items: list[tuple[str, str]]) -> None:
        """Show popup with items. Each item is (value, display)."""
        self._items = items[:8]  # Limit to 8 items
        self._selected_index = 0
        self.is_visible = True
        self.run_worker(self._render_items())

    def hide(self) -> None:
        """Hide the popup."""
        self.is_visible = False
        self._items = []

    def watch_is_visible(self, value: bool) -> None:
        self.set_class(value, "--visible")

    async def _render_items(self) -> None:
        """Render item list asynchronously."""
        try:
            container = self.query_one("#autocomplete-list", Vertical)
            await container.remove_children()
            
            items_to_mount = []
            for i, (value, display) in enumerate(self._items):
                item = AutocompleteItem(value, display)
                item.is_selected = (i == self._selected_index)
                items_to_mount.append(item)
            
            if items_to_mount:
                await container.mount_all(items_to_mount)
        except Exception:
            pass

    def move_selection(self, delta: int) -> None:
        """Move selection up or down."""
        if not self._items:
            return
        self._selected_index = (self._selected_index + delta) % len(self._items)
        self._update_selection()

    def _update_selection(self) -> None:
        """Update visual selection."""
        try:
            items = self.query(AutocompleteItem)
            for i, item in enumerate(items):
                item.is_selected = (i == self._selected_index)
        except Exception:
            pass

    def confirm_selection(self) -> bool:
        """Confirm current selection. Returns True if item was selected."""
        if not self._items or not self.is_visible:
            return False
        value, display = self._items[self._selected_index]
        self.post_message(self.ItemSelected(value, display))
        self.hide()
        return True

    def on_autocomplete_item_selected(self, message: AutocompleteItem.Selected) -> None:
        """Handle item click."""
        self.post_message(self.ItemSelected(message.value, message.display))
        self.hide()


# Available slash commands
SLASH_COMMANDS = [
    ("/img", "/img - 发送剪贴板图片"),
    ("/img ", "/img <路径> - 发送本地图片"),
    ("/reply ", "/reply <消息ID> - 回复消息"),
]
