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

    def add_friend(self, friend: FriendInfo) -> Session:
        """Add a friend as a session."""
        session = Session(
            session_id=friend.session_id,
            name=friend.display_name,
            is_group=False,
            target_id=friend.user_id,
        )
        self.sessions[session.session_id] = session
        return session

    def add_group(self, group: GroupInfo) -> Session:
        """Add a group as a session."""
        session = Session(
            session_id=group.session_id,
            name=group.group_name,
            is_group=True,
            target_id=group.group_id,
        )
        self.sessions[session.session_id] = session
        return session

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
        if session_id in self.sessions:
            self.sessions[session_id].last_message = message[:30]


# Global state instance
session_state = SessionState()
