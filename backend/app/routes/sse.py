"""
SSE 端点
"""
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.sse_bus import stream

router = APIRouter(prefix="/api/stream", tags=["stream"])


@router.get("")
async def event_stream():
    return EventSourceResponse(stream())
