"""
抽奖 REST API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.lottery_engine import get_engine
from app.sse_bus import publish

router = APIRouter(prefix="/api/draw", tags=["draw"])


@router.post("")
async def draw_prize(payload: dict, db: Session = Depends(get_db)):
    """
    body: {"prize_id": int}
    返回: 中奖结果 dict / 409 表示已抽完
    """
    prize_id = payload.get("prize_id")
    if not isinstance(prize_id, int):
        raise HTTPException(400, "prize_id 必填且为整数")

    eng = get_engine()
    can, msg = eng.can_draw(prize_id, db)
    if not can:
        raise HTTPException(409, msg)

    out = await eng.draw(prize_id, db)
    if out is None:
        raise HTTPException(409, "抽奖失败: 奖池为空或奖项已满")

    # 广播给所有 SSE 订阅者
    await publish("draw_completed", out)

    return out
