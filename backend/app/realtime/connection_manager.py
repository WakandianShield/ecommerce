from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        self._connections[session_id] = websocket

    def disconnect(self, session_id: str) -> None:
        self._connections.pop(session_id, None)

    async def send_json(self, session_id: str, payload: dict) -> None:
        websocket = self._connections.get(session_id)
        if websocket:
            await websocket.send_json(payload)
