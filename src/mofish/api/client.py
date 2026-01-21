"""WebSocket client for NapCat OneBot 11 API."""

import asyncio
import json
import uuid
from typing import Any, Callable

import websockets
from websockets.asyncio.client import ClientConnection

from mofish.config import config


class OneBotClient:
    """Async WebSocket client for OneBot 11 protocol."""

    def __init__(self) -> None:
        self._ws: ClientConnection | None = None
        self._connected = False
        self._pending_requests: dict[str, asyncio.Future[dict[str, Any]]] = {}
        self._event_handlers: list[Callable[[dict[str, Any]], None]] = []
        self._reconnect_task: asyncio.Task[None] | None = None

    @property
    def is_connected(self) -> bool:
        """Check if client is connected."""
        return self._connected and self._ws is not None

    def on_event(self, handler: Callable[[dict[str, Any]], None]) -> None:
        """Register an event handler."""
        self._event_handlers.append(handler)

    async def connect(self) -> bool:
        """Connect to NapCat WebSocket server."""
        try:
            headers = {}
            if config.ws_token:
                headers["Authorization"] = f"Bearer {config.ws_token}"

            self._ws = await websockets.connect(
                config.ws_url,
                additional_headers=headers,
            )
            self._connected = True

            # Start message receiver
            asyncio.create_task(self._receive_loop())

            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            self._connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from server."""
        self._connected = False
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def _receive_loop(self) -> None:
        """Receive and dispatch messages."""
        if not self._ws:
            return

        try:
            async for message in self._ws:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    continue
        except websockets.ConnectionClosed:
            self._connected = False
        except Exception as e:
            print(f"[ERROR] Receive error: {e}")
            self._connected = False

    async def _handle_message(self, data: dict[str, Any]) -> None:
        """Handle incoming message."""
        # Check if it's a response to our request
        if "echo" in data:
            echo = data["echo"]
            if echo in self._pending_requests:
                future = self._pending_requests.pop(echo)
                if not future.done():
                    future.set_result(data)
                return

        # It's an event, dispatch to handlers
        for handler in self._event_handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"[ERROR] Event handler error: {e}")

    async def call_api(
        self, action: str, params: dict[str, Any] | None = None, timeout: float = 10.0
    ) -> dict[str, Any]:
        """Call OneBot API action."""
        if not self.is_connected:
            raise ConnectionError("Not connected to server")

        echo = str(uuid.uuid4())
        request = {
            "action": action,
            "params": params or {},
            "echo": echo,
        }

        future: asyncio.Future[dict[str, Any]] = asyncio.get_event_loop().create_future()
        self._pending_requests[echo] = future

        try:
            await self._ws.send(json.dumps(request))  # type: ignore
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            self._pending_requests.pop(echo, None)
            raise TimeoutError(f"API call '{action}' timed out")


# Global client instance
client = OneBotClient()
