"""
SSE 事件总线 (进程内 pub/sub)

- subscribe() 返回一个 asyncio.Queue
- publish(event, data) 广播到所有订阅者
- 慢消费者 (queue 满) 时丢最旧事件, 避免内存堆积
"""
import asyncio
import json
import time
from typing import Any, AsyncGenerator, Dict, Set

_subs: Set[asyncio.Queue] = set()
QUEUE_MAX = 64


def subscribe() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue(maxsize=QUEUE_MAX)
    _subs.add(q)
    return q


def unsubscribe(q: asyncio.Queue) -> None:
    _subs.discard(q)


async def publish(event: str, data: Dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False)
    dead: list[asyncio.Queue] = []
    for q in list(_subs):
        try:
            if q.full():
                # 丢最旧
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
            await q.put((event, payload))
        except Exception:
            dead.append(q)
    for q in dead:
        _subs.discard(q)


async def stream() -> AsyncGenerator[dict, None]:
    """sse-starlette 用的 generator, yield {"event": ..., "data": ...} 字典"""
    q = subscribe()
    try:
        # 发送一条 hello 事件, 让客户端确认连接
        yield {"event": "connected", "data": json.dumps({"ts": time.time()})}
        while True:
            event, payload = await q.get()
            yield {"event": event, "data": payload}
    finally:
        unsubscribe(q)
