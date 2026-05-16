"""NEXUS OS — WebSocket Real-Time Event System"""

import asyncio
import json
import uuid
from typing import Any, Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger()
router = APIRouter()


class ConnectionManager:
    """Manages active WebSocket connections by channel."""

    def __init__(self):
        # channel_id -> set of websockets
        self.channels: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str):
        await websocket.accept()
        self.channels.setdefault(channel, set()).add(websocket)
        logger.info("🔌 WebSocket connected", channel=channel, connections=len(self.channels[channel]))

    def disconnect(self, websocket: WebSocket, channel: str):
        if channel in self.channels:
            self.channels[channel].discard(websocket)
        logger.info("🔌 WebSocket disconnected", channel=channel)

    async def broadcast(self, channel: str, message: Dict[str, Any]):
        """Broadcast message to all clients in a channel."""
        if channel not in self.channels:
            return
        dead = set()
        for ws in self.channels[channel]:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.channels[channel].discard(ws)

    async def send_to(self, websocket: WebSocket, message: Dict[str, Any]):
        await websocket.send_text(json.dumps(message))


manager = ConnectionManager()


@router.websocket("/engineering/{task_id}")
async def engineering_stream(websocket: WebSocket, task_id: str):
    """Stream real-time engineering pipeline events for a task."""
    await manager.connect(websocket, f"task:{task_id}")
    try:
        await manager.send_to(websocket, {
            "type": "connected",
            "task_id": task_id,
            "message": "Connected to NEXUS OS engineering stream",
        })
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await manager.send_to(websocket, {"type": "pong", "task_id": task_id})
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"task:{task_id}")


@router.websocket("/agents")
async def agents_stream(websocket: WebSocket):
    """Stream real-time agent execution events across all tasks."""
    await manager.connect(websocket, "agents:global")
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg.get("type") == "ping":
                await manager.send_to(websocket, {"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "agents:global")


@router.websocket("/monitoring")
async def monitoring_stream(websocket: WebSocket):
    """Stream real-time infrastructure monitoring events."""
    await manager.connect(websocket, "monitoring:global")
    try:
        while True:
            await asyncio.sleep(5)
            # Emit synthetic heartbeat metrics
            await manager.send_to(websocket, {
                "type": "metrics_snapshot",
                "metrics": {
                    "agents_active": 0,
                    "tasks_running": 0,
                    "deployments_pending": 0,
                    "incidents_open": 0,
                }
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, "monitoring:global")


async def emit_agent_event(task_id: str, agent: str, event_type: str, payload: Dict):
    """Emit an agent lifecycle event to connected clients."""
    await manager.broadcast(f"task:{task_id}", {
        "type": "agent_event",
        "event": event_type,
        "agent": agent,
        "task_id": task_id,
        "payload": payload,
    })
    await manager.broadcast("agents:global", {
        "type": "agent_event",
        "event": event_type,
        "agent": agent,
        "task_id": task_id,
    })
