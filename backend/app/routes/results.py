"""
中奖结果 REST API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Result, Prize
from app.sse_bus import publish

router = APIRouter(prefix="/api/results", tags=["results"])


@router.get("")
def list_results(db: Session = Depends(get_db)) -> List[dict]:
    rows = db.query(Result).order_by(Result.timestamp.desc()).all()
    return [r.to_dict() for r in rows]


@router.delete("")
async def clear_results(db: Session = Depends(get_db)) -> dict:
    """清空中奖结果 + 重置所有奖项的 drawn 计数"""
    deleted = db.query(Result).delete()
    for p in db.query(Prize).all():
        p.drawn = 0
    db.commit()
    await publish("reset", {"deleted": deleted})
    return {"deleted": deleted}
