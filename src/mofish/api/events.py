"""OneBot 11 event types and parsing."""

from dataclasses import dataclass
from typing import Any


@dataclass
class MessageSegment:
    """A segment of a message (text, image, etc.)."""

    type: str
    data: dict[str, Any]

    @property
    def text(self) -> str:
        """Get text content if this is a text segment."""
        if self.type == "text":
            return self.data.get("text", "")
        return ""

    @property
    def is_image(self) -> bool:
        """Check if this is an image segment."""
        return self.type == "image"

    @property
    def is_at(self) -> bool:
        """Check if this is an @ mention."""
        return self.type == "at"

    @property
    def at_qq(self) -> str:
        """Get QQ number being mentioned."""
        if self.type == "at":
            return self.data.get("qq", "")
        return ""


@dataclass
class MessageEvent:
    """Parsed message event."""

    message_type: str  # "private" or "group"
    sub_type: str
    message_id: int
    user_id: int
    group_id: int | None
    sender_nickname: str
    sender_card: str  # group card name
    raw_message: str
    segments: list[MessageSegment]
    time: int

    @property
    def display_name(self) -> str:
        """Get display name (card > nickname)."""
        return self.sender_card or self.sender_nickname

    @property
    def plain_text(self) -> str:
        """Get plain text content."""
        return "".join(seg.text for seg in self.segments)

    @property
    def has_image(self) -> bool:
        """Check if message contains images."""
        return any(seg.is_image for seg in self.segments)

    @property
    def is_private(self) -> bool:
        """Check if this is a private message."""
        return self.message_type == "private"

    @property
    def is_group(self) -> bool:
        """Check if this is a group message."""
        return self.message_type == "group"

    @property
    def session_id(self) -> str:
        """Get unique session identifier."""
        if self.is_group and self.group_id:
            return f"group_{self.group_id}"
        return f"private_{self.user_id}"


def parse_message_event(data: dict[str, Any]) -> MessageEvent | None:
    """Parse raw event data into MessageEvent."""
    if data.get("post_type") != "message":
        return None

    # Parse message segments (Array format)
    raw_segments = data.get("message", [])
    segments: list[MessageSegment] = []

    if isinstance(raw_segments, list):
        for seg in raw_segments:
            if isinstance(seg, dict):
                segments.append(MessageSegment(
                    type=seg.get("type", "unknown"),
                    data=seg.get("data", {}),
                ))
    elif isinstance(raw_segments, str):
        # String format fallback
        segments.append(MessageSegment(type="text", data={"text": raw_segments}))

    sender = data.get("sender", {})

    return MessageEvent(
        message_type=data.get("message_type", ""),
        sub_type=data.get("sub_type", ""),
        message_id=data.get("message_id", 0),
        user_id=data.get("user_id", 0),
        group_id=data.get("group_id"),
        sender_nickname=sender.get("nickname", ""),
        sender_card=sender.get("card", ""),
        raw_message=data.get("raw_message", ""),
        segments=segments,
        time=data.get("time", 0),
    )


def create_self_message(
    text: str,
    session_id: str,
    nickname: str = "我",
) -> MessageEvent:
    """Create a local echo message for sent messages."""
    import time as time_module

    is_group = session_id.startswith("group_")
    target_id = int(session_id.split("_")[1])

    # For private chat, set user_id to target so session_id matches
    # For group chat, set group_id to target
    return MessageEvent(
        message_type="group" if is_group else "private",
        sub_type="normal",
        message_id=0,
        user_id=target_id if not is_group else 0,  # Match session_id for private
        group_id=target_id if is_group else None,
        sender_nickname=nickname,
        sender_card="",
        raw_message=text,
        segments=[MessageSegment(type="text", data={"text": text})],
        time=int(time_module.time()),
    )


@dataclass
class FriendInfo:
    """Friend information."""

    user_id: int
    nickname: str
    remark: str

    @property
    def display_name(self) -> str:
        """Get display name (remark > nickname)."""
        return self.remark or self.nickname

    @property
    def session_id(self) -> str:
        """Get session identifier."""
        return f"private_{self.user_id}"


@dataclass
class GroupInfo:
    """Group information."""

    group_id: int
    group_name: str
    member_count: int

    @property
    def session_id(self) -> str:
        """Get session identifier."""
        return f"group_{self.group_id}"


def parse_friend_list(data: list[dict[str, Any]]) -> list[FriendInfo]:
    """Parse friend list response."""
    return [
        FriendInfo(
            user_id=f.get("user_id", 0),
            nickname=f.get("nickname", ""),
            remark=f.get("remark", ""),
        )
        for f in data
    ]


def parse_group_list(data: list[dict[str, Any]]) -> list[GroupInfo]:
    """Parse group list response."""
    return [
        GroupInfo(
            group_id=g.get("group_id", 0),
            group_name=g.get("group_name", ""),
            member_count=g.get("member_count", 0),
        )
        for g in data
    ]
