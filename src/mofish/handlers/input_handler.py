"""Handler for message input submission."""

import re
from typing import TYPE_CHECKING, Any

from textual.app import App
from textual.widgets import Static

from mofish.api import actions
from mofish.api.events import create_self_message
from mofish.state.member_cache import member_cache
from mofish.state.session import session_state
from mofish.ui.chatlog import ChatLog
from mofish.utils.commands import build_message_array, parse_input

if TYPE_CHECKING:
    from mofish.app import MofishApp


class InputHandler:
    """Handles message input submission logic."""

    async def handle_submit(self, text: str, app: App) -> None:
        """Handle submitted message text."""
        session = session_state.get_active_session()
        if not session:
            return

        # Parse commands (@, /reply, /img)
        commands = parse_input(text)

        # Build message array
        msg_array = build_message_array(commands)

        if not msg_array:
            return

        # Determine display text for echo
        display_text = text
        has_image = any(cmd.command_type == "image" for cmd in commands)
        if has_image:
            display_text = "[发送图片]"
        elif session.is_group:
            # 将 @QQ号 替换为 @群昵称 喵～
            display_text = self._replace_at_with_nickname(text, session.target_id)

        # Send message
        try:
            if session.is_group:
                await actions.send_group_msg(session.target_id, msg_array)
            else:
                await actions.send_private_msg(session.target_id, msg_array)

            # Add local echo (show our own message)
            self_msg = create_self_message(display_text, session.session_id, "我")
            try:
                chat_log = app.query_one("#chat-log", ChatLog)
                chat_log.add_message(self_msg)
            except Exception:
                pass

        except Exception as e:
            try:
                status = app.query_one("#status-bar", Static)
                status.update(f"[#ff4444]Send failed: {e}[/]")
            except Exception:
                pass

    def _replace_at_with_nickname(self, text: str, group_id: int) -> str:
        """将文本中的 @QQ号 替换为 @群昵称."""
        def replace_at(match: re.Match) -> str:
            qq = match.group(1)
            if qq == "all":
                return "@全体成员"
            display = member_cache.get_display_name(group_id, qq)
            return f"@{display}" if display else f"@{qq}"

        return re.sub(r"@(\d+|all)", replace_at, text)

