"""Session state management."""

from dataclasses import dataclass, field

from mofish.api.events import FriendInfo, GroupInfo


@dataclass
class Session:
    """Represents a chat session."""

    session_id: str
    name: str
    is_group: bool
    target_id: int  # user_id or group_id
    unread_count: int = 0
    last_message: str = ""


@dataclass
class SessionState:
    """Manages all sessions."""

    sessions: dict[str, Session] = field(default_factory=dict)
    active_session_id: str = ""

    def add_session(
        self, session_id: str, name: str, is_group: bool, target_id: int
    ) -> Session:
        """Add a session (friend or group)."""
        session = Session(
            session_id=session_id,
            name=name,
            is_group=is_group,
            target_id=target_id,
        )
        self.sessions[session.session_id] = session
        return session

    def add_friend(self, friend: FriendInfo) -> Session:
        """Add a friend as a session."""
        return self.add_session(
            friend.session_id, friend.display_name, False, friend.user_id
        )

    def add_group(self, group: GroupInfo) -> Session:
        """Add a group as a session."""
        return self.add_session(
            group.session_id, group.group_name, True, group.group_id
        )

    def get_session(self, session_id: str) -> Session | None:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def get_active_session(self) -> Session | None:
        """Get the currently active session."""
        return self.sessions.get(self.active_session_id)

    def set_active(self, session_id: str) -> bool:
        """Set the active session."""
        if session_id in self.sessions:
            self.active_session_id = session_id
            # Clear unread count when session becomes active
            self.sessions[session_id].unread_count = 0
            return True
        return False

    def increment_unread(self, session_id: str) -> None:
        """Increment unread count for a session."""
        if session_id in self.sessions:
            self.sessions[session_id].unread_count += 1

    def update_last_message(self, session_id: str, message: str) -> None:
        """Update last message preview."""
        from mofish.config import config

        if session_id in self.sessions:
            self.sessions[session_id].last_message = message[:config.preview_length]


# Global state instance
session_state = SessionState()
