from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if user_id not in self._connections:
            self._connections[user_id] = []
        self._connections[user_id].append(websocket)

    def get_connections(self, user_id: str) -> list[WebSocket]:
        return self._connections.get(user_id, [])

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        if user_id in self._connections:
            self._connections[user_id] = [ws for ws in self._connections[user_id] if ws != websocket]
            if not self._connections[user_id]:
                del self._connections[user_id]

    async def send_personal_message(self, data: dict, websocket: WebSocket) -> None:
        import json
        await websocket.send_text(json.dumps(data, ensure_ascii=False))

    async def broadcast_to_user(self, user_id: str, data: dict) -> None:
        import json
        if user_id in self._connections:
            for ws in self._connections[user_id]:
                await ws.send_text(json.dumps(data, ensure_ascii=False))


manager = ConnectionManager()
