from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._admin_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, session_id: str) -> None:
        await websocket.accept()
        self._connections.setdefault(session_id, set()).add(websocket)

    async def connect_admin(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._admin_connections.add(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket | None = None) -> None:
        if websocket is None:
            self._connections.pop(session_id, None)
            return
        sockets = self._connections.get(session_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self._connections.pop(session_id, None)

    def disconnect_admin(self, websocket: WebSocket) -> None:
        self._admin_connections.discard(websocket)

    async def send_json(self, session_id: str, payload: dict) -> None:
        await self.broadcast_json(session_id, payload)

    async def broadcast_json(self, session_id: str, payload: dict) -> None:
        sockets = list(self._connections.get(session_id, set()))
        for websocket in sockets:
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect(session_id, websocket)

    async def broadcast_admin_json(self, payload: dict) -> None:
        for websocket in list(self._admin_connections):
            try:
                await websocket.send_json(payload)
            except Exception:
                self.disconnect_admin(websocket)
