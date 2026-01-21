"""Boss mode - fake screen for emergency hiding."""

import random
from pathlib import Path

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static


# Fake log templates
FAKE_WEBPACK_LOGS = [
    "[#888888]webpack 5.89.0 compiled successfully in 1247 ms[/]",
    "[#888888]asset main.js 1.24 MiB [emitted] (name: main)[/]",
    "[#888888]asset vendors.js 892 KiB [emitted] (name: vendors)[/]",
    "[#ffaa00]WARNING in ./src/components/App.tsx[/]",
    "[#888888]Module Warning (from ./node_modules/eslint-loader/dist/cjs.js):[/]",
    "[#ffaa00]  Line 42:  'unused' is defined but never used  no-unused-vars[/]",
    "[#888888]webpack compiled with 1 warning[/]",
    "[#888888]  [0] ./src/index.tsx 2.3 KiB {main}[/]",
    "[#888888]  [1] ./src/App.tsx 15.6 KiB {main}[/]",
    "[#888888]  [2] ./node_modules/react/index.js 7.2 KiB {vendors}[/]",
    "[#00ff00]✓ Compiled successfully.[/]",
    "[#888888]Watching for file changes...[/]",
]

FAKE_NPM_LOGS = [
    "[#888888]npm WARN deprecated @types/react@17.0.0: Use @types/react@18[/]",
    "[#888888]added 1247 packages in 45s[/]",
    "[#888888]156 packages are looking for funding[/]",
    "[#888888]  run `npm fund` for details[/]",
    "[#888888]Installing dependencies from package-lock.json[/]",
    "[#00ff00]✓ Dependencies installed successfully[/]",
    "[#888888]> node scripts/postinstall.js[/]",
    "[#888888]Rebuilding node-sass...[/]",
    "[#888888]Binary found at /node_modules/node-sass/vendor/...[/]",
]

FAKE_JAVA_LOGS = [
    "[#ff4444]Exception in thread \"main\" java.lang.NullPointerException[/]",
    "[#888888]    at com.example.service.UserService.getUser(UserService.java:42)[/]",
    "[#888888]    at com.example.controller.UserController.handleRequest(UserController.java:87)[/]",
    "[#888888]    at sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)[/]",
    "[#888888]    at org.springframework.web.servlet.FrameworkServlet.service(FrameworkServlet.java:897)[/]",
    "[#888888]Caused by: java.sql.SQLException: Connection refused[/]",
    "[#888888]    at com.mysql.jdbc.ConnectionImpl.createNewIO(ConnectionImpl.java:2181)[/]",
    "[#ffaa00][WARN] HikariPool-1 - Connection is not available, request timed out after 30000ms.[/]",
    "[#888888][INFO] BUILD SUCCESS[/]",
    "[#888888][INFO] Total time: 12.345 s[/]",
]

FAKE_PING_LOGS = [
    "[#888888]PING 192.168.1.1 (192.168.1.1): 56 data bytes[/]",
    "[#888888]64 bytes from 192.168.1.1: icmp_seq=0 ttl=64 time=1.234 ms[/]",
    "[#888888]64 bytes from 192.168.1.1: icmp_seq=1 ttl=64 time=0.987 ms[/]",
    "[#888888]64 bytes from 192.168.1.1: icmp_seq=2 ttl=64 time=1.123 ms[/]",
    "[#888888]64 bytes from 192.168.1.1: icmp_seq=3 ttl=64 time=0.856 ms[/]",
    "[#888888]--- 192.168.1.1 ping statistics ---[/]",
    "[#888888]4 packets transmitted, 4 packets received, 0.0% packet loss[/]",
    "[#888888]round-trip min/avg/max/stddev = 0.856/1.050/1.234/0.138 ms[/]",
]


class BossMode(Widget):
    """Fake screen overlay for emergency hiding."""

    DEFAULT_CSS = """
    BossMode {
        background: #0a0a0a;
        padding: 1 2;
        layer: boss;
    }

    BossMode #boss-header {
        color: #00ff00;
        text-style: bold;
        padding-bottom: 1;
    }

    BossMode #boss-log {
        background: #0a0a0a;
        height: 100%;
    }
    """

    is_active: reactive[bool] = reactive(False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._log_type = "webpack"

    def compose(self) -> ComposeResult:
        yield Static("$ npm run build", id="boss-header")
        yield VerticalScroll(id="boss-log")

    def on_mount(self) -> None:
        """Initialize with some fake logs."""
        self._populate_logs()

    def _populate_logs(self) -> None:
        """Fill screen with fake logs."""
        log_sets = {
            "webpack": FAKE_WEBPACK_LOGS,
            "npm": FAKE_NPM_LOGS,
            "java": FAKE_JAVA_LOGS,
            "ping": FAKE_PING_LOGS,
        }

        # Randomly pick a log type
        self._log_type = random.choice(list(log_sets.keys()))
        logs = log_sets[self._log_type]

        # Update header based on type
        headers = {
            "webpack": "$ npm run build",
            "npm": "$ npm install",
            "java": "$ mvn clean install",
            "ping": "$ ping 192.168.1.1",
        }

        try:
            header = self.query_one("#boss-header", Static)
            header.update(headers.get(self._log_type, "$ command"))

            scroll = self.query_one("#boss-log", VerticalScroll)
            scroll.remove_children()

            # Add random amount of logs to fill screen
            for _ in range(30):
                log_line = random.choice(logs)
                scroll.mount(Static(log_line, markup=True))
        except Exception:
            pass

    def refresh_logs(self) -> None:
        """Refresh with new random logs."""
        self._populate_logs()

    def watch_is_active(self, value: bool) -> None:
        """Handle visibility change."""
        self.display = value
        if value:
            self.refresh_logs()
