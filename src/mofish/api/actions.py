"""OneBot API actions wrapper."""

from typing import Any

from mofish.api.client import client
from mofish.api.events import (
    FriendInfo,
    GroupInfo,
    parse_friend_list,
    parse_group_list,
)


async def _call_api_data(
    action: str, params: dict | None = None, default: Any = None
) -> Any:
    """Call API and return data if successful, else default."""
    result = await client.call_api(action, params or {})
    if result.get("status") == "ok":
        return result.get("data", default if default is not None else {})
    return default if default is not None else {}


async def get_friend_list() -> list[FriendInfo]:
    """Get friend list."""
    data = await _call_api_data("get_friend_list", default=[])
    return parse_friend_list(data)


async def get_group_list() -> list[GroupInfo]:
    """Get group list."""
    data = await _call_api_data("get_group_list", default=[])
    return parse_group_list(data)


async def send_private_msg(
    user_id: int, message: str | list[dict[str, Any]]
) -> dict[str, Any]:
    """Send private message. Message can be string or array format."""
    return await client.call_api(
        "send_private_msg",
        {"user_id": user_id, "message": message},
    )


async def send_group_msg(
    group_id: int, message: str | list[dict[str, Any]]
) -> dict[str, Any]:
    """Send group message. Message can be string or array format."""
    return await client.call_api(
        "send_group_msg",
        {"group_id": group_id, "message": message},
    )


async def get_login_info() -> dict[str, Any]:
    """Get bot login info."""
    return await _call_api_data("get_login_info", default={})


async def get_group_member_list(group_id: int) -> list[dict[str, Any]]:
    """Get group member list."""
    return await _call_api_data("get_group_member_list", {"group_id": group_id}, default=[])


async def get_group_msg_history(group_id: int) -> list[dict[str, Any]]:
    """Get group message history (latest 20)."""
    result = await client.call_api(
        "get_group_msg_history",
        {"group_id": group_id, "count": 20},
    )
    if result.get("status") == "ok":
        return result.get("data", {}).get("messages", [])
    return []


async def get_friend_msg_history(user_id: int) -> list[dict[str, Any]]:
    """Get friend message history (latest 20)."""
    result = await client.call_api(
        "get_friend_msg_history",
        {"user_id": user_id, "count": 20},
    )
    if result.get("status") == "ok":
        return result.get("data", {}).get("messages", [])
    return []
