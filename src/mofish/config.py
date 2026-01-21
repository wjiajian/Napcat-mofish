"""Configuration management for Mofish client."""

from dataclasses import dataclass, field


@dataclass
class Config:
    """Application configuration."""

    # NapCat WebSocket settings
    ws_host: str = "127.0.0.1"
    ws_port: int = 3001
    ws_token: str = "GKUdr5U8rbWb(*8u"
    heartbeat_interval: int = 30000  # ms

    # Display settings
    prompt_style: str = "admin@local:~$"  # or ">>>"
    window_title: str = "node_modules install"

    # Highlight keywords (messages containing these will be highlighted)
    highlight_keywords: list[str] = field(
        default_factory=lambda: ["吃饭", "下班", "开会", "加班"]
    )

    # Your name for mention detection
    my_name: str = ""

    # Message buffer size per session
    message_buffer_size: int = 100

    @property
    def ws_url(self) -> str:
        """Get full WebSocket URL."""
        return f"ws://{self.ws_host}:{self.ws_port}"


# Global config instance
config = Config()
