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
            # 将 @QQ号 替换为群昵称，/reply 消息ID 替换为发送者昵称喵～
            display_text = self._replace_qq_with_nickname(text, session.target_id, app)

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

    def _replace_qq_with_nickname(self, text: str, group_id: int, app: App) -> str:
        """将文本中的 @QQ号 替换为群昵称，/reply 消息ID 替换为发送者昵称."""
        from mofish.ui.chatlog import ChatLog
        
        def replace_at(match: re.Match) -> str:
            """替换 @QQ号 为群昵称."""
            return member_cache.format_at_display(group_id, match.group(1))
        
        def replace_reply(match: re.Match) -> str:
            """替换 /reply 消息ID 为发送者昵称."""
            msg_id_str = match.group(1)
            rest = match.group(2)
            try:
                msg_id = int(msg_id_str)
                chat_log = app.query_one("#chat-log", ChatLog)
                msg_event = chat_log.get_message_by_id(msg_id)
                if msg_event:
                    # 用发送者昵称替换消息 ID
                    return f"/reply @{msg_event.display_name}{rest}"
            except Exception:
                pass
            return match.group(0)  # 未找到则保持原样
        
        # 先处理 /reply 消息ID
        result = re.sub(r"/reply (\d+)(\s*)", replace_reply, text)
        # 再处理 @QQ号
        result = re.sub(r"@(\d+|all)", replace_at, result)
        return result
