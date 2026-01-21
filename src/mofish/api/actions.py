"""OneBot API actions wrapper."""

from typing import Any

from mofish.api.client import client
from mofish.api.events import (
    FriendInfo,
    GroupInfo,
    parse_friend_list,
    parse_group_list,
)


async def get_friend_list() -> list[FriendInfo]:
    """Get friend list."""
    result = await client.call_api("get_friend_list")
    if result.get("status") == "ok":
        return parse_friend_list(result.get("data", []))
    return []


async def get_group_list() -> list[GroupInfo]:
    """Get group list."""
    result = await client.call_api("get_group_list")
    if result.get("status") == "ok":
        return parse_group_list(result.get("data", []))
    return []


async def send_private_msg(user_id: int, message: str) -> dict[str, Any]:
    """Send private message."""
    return await client.call_api(
        "send_private_msg",
        {"user_id": user_id, "message": message},
    )


async def send_group_msg(group_id: int, message: str) -> dict[str, Any]:
    """Send group message."""
    return await client.call_api(
        "send_group_msg",
        {"group_id": group_id, "message": message},
    )


async def get_login_info() -> dict[str, Any]:
    """Get bot login info."""
    result = await client.call_api("get_login_info")
    if result.get("status") == "ok":
        return result.get("data", {})
    return {}
