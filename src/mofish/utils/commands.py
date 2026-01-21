"""Command parser for special message commands."""

import base64
import io
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ParsedCommand:
    """Parsed command result."""

    command_type: str  # "text", "at", "reply", "image"
    content: str = ""
    target_qq: str = ""  # For @ command
    reply_id: int = 0  # For reply command
    image_data: str = ""  # Base64 image data
    image_file: str = ""  # Image file path


def parse_input(text: str) -> list[ParsedCommand]:
    """Parse input text for special commands.

    Supported commands:
    - @123456 or @all - Mention someone
    - /reply 123456 message - Reply to a message
    - /img or /image - Send clipboard image
    - /img path/to/file - Send image from file
    """
    commands: list[ParsedCommand] = []

    # Check for /reply command
    reply_match = re.match(r"^/reply\s+(\d+)\s*(.*)", text, re.DOTALL)
    if reply_match:
        msg_id = int(reply_match.group(1))
        remaining = reply_match.group(2).strip()
        commands.append(ParsedCommand(
            command_type="reply",
            reply_id=msg_id,
        ))
        if remaining:
            commands.extend(parse_input(remaining))
        return commands

    # Check for /img command
    img_match = re.match(r"^/img(?:age)?\s*(.*)", text, re.IGNORECASE)
    if img_match:
        path_arg = img_match.group(1).strip()
        if path_arg and os.path.isfile(path_arg):
            # Send file
            commands.append(ParsedCommand(
                command_type="image",
                image_file=path_arg,
            ))
        else:
            # Try clipboard
            img_data = get_clipboard_image()
            if img_data:
                commands.append(ParsedCommand(
                    command_type="image",
                    image_data=img_data,
                ))
        return commands

    # Parse @ mentions in text
    parts = re.split(r"(@\d+|@all)", text)
    for part in parts:
        if not part:
            continue
        if part.startswith("@"):
            qq = part[1:]
            commands.append(ParsedCommand(
                command_type="at",
                target_qq=qq,
            ))
        else:
            commands.append(ParsedCommand(
                command_type="text",
                content=part,
            ))

    return commands


def get_clipboard_image() -> str:
    """Get image from clipboard as base64 string."""
    try:
        from PIL import ImageGrab

        img = ImageGrab.grabclipboard()
        if img is None:
            return ""

        # Convert to JPEG and base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")
    except Exception:
        return ""


def build_message_array(commands: list[ParsedCommand]) -> list[dict[str, Any]]:
    """Build OneBot message array from parsed commands."""
    message: list[dict[str, Any]] = []

    for cmd in commands:
        if cmd.command_type == "text":
            message.append({
                "type": "text",
                "data": {"text": cmd.content},
            })
        elif cmd.command_type == "at":
            message.append({
                "type": "at",
                "data": {"qq": cmd.target_qq},
            })
        elif cmd.command_type == "reply":
            message.append({
                "type": "reply",
                "data": {"id": str(cmd.reply_id)},
            })
        elif cmd.command_type == "image":
            if cmd.image_data:
                message.append({
                    "type": "image",
                    "data": {"file": f"base64://{cmd.image_data}"},
                })
            elif cmd.image_file:
                # Use file:// protocol for local files
                abs_path = os.path.abspath(cmd.image_file)
                message.append({
                    "type": "image",
                    "data": {"file": f"file:///{abs_path}"},
                })

    return message
