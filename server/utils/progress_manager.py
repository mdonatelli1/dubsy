from typing import Any, Dict, Set

from fastapi import WebSocket


class ProgressManager:
    """Centralise WebSocket subscriptions by job_id and broadcasts progress events."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, Set[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if job_id not in self._subscribers:
            self._subscribers[job_id] = set()
        self._subscribers[job_id].add(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        if job_id in self._subscribers:
            self._subscribers[job_id].discard(websocket)
            if not self._subscribers[job_id]:
                del self._subscribers[job_id]

    async def send(self, job_id: str, event: str, payload: Any | None = None) -> None:
        if job_id not in self._subscribers:
            return
        message = {"type": event}
        if payload is not None:
            message["data"] = payload
        dead: Set[WebSocket] = set()
        for ws in self._subscribers[job_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(job_id, ws)


progress_manager = ProgressManager()
