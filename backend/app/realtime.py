from typing import Dict, Set, Any
from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(user_id, set()).add(ws)

    def disconnect(self, user_id: int, ws: WebSocket):
        if user_id in self.active:
            self.active[user_id].discard(ws)
            if not self.active[user_id]:
                del self.active[user_id]

    async def send(self, user_id: int, event: str, data: Any):
        if user_id not in self.active:
            return
        payload = json.dumps({"event": event, "data": data}, default=str)
        for ws in list(self.active[user_id]):
            try:
                await ws.send_text(payload)
            except Exception:
                self.disconnect(user_id, ws)

manager = ConnectionManager()
