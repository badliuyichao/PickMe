"""
奖项管理 REST API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Prize
from app.schemas import PrizeCreate, PrizeUpdate

router = APIRouter(prefix="/api/prizes", tags=["prizes"])


# 6 预设色（沿用原桌面版）
DEFAULT_COLORS = [
    "#FFD700",  # 金
    "#C0C0C0",  # 银
    "#CD7F32",  # 铜
    "#00fff5",  # 霓虹蓝
    "#ff00ff",  # 霓虹紫
    "#ff0055",  # 霓虹红
]


@router.get("")
def list_prizes(db: Session = Depends(get_db)) -> List[dict]:
    rows = db.query(Prize).order_by(Prize.id).all()
    return [p.to_dict() for p in rows]


@router.get("/defaults")
def get_default_colors() -> dict:
    return {"colors": DEFAULT_COLORS}


@router.post("")
def create_prize(payload: PrizeCreate, db: Session = Depends(get_db)) -> dict:
    p = Prize(name=payload.name.strip(), count=payload.count, color=payload.color)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p.to_dict()


@router.put("/{prize_id}")
def update_prize(prize_id: int, payload: PrizeUpdate, db: Session = Depends(get_db)) -> dict:
    p = db.get(Prize, prize_id)
    if not p:
        raise HTTPException(404, "奖项不存在")
    if payload.name is not None:
        p.name = payload.name.strip()
    if payload.count is not None:
        p.count = payload.count
    if payload.color is not None:
        p.color = payload.color
    db.commit()
    db.refresh(p)
    return p.to_dict()


@router.delete("/{prize_id}")
def delete_prize(prize_id: int, db: Session = Depends(get_db)) -> dict:
    p = db.get(Prize, prize_id)
    if not p:
        raise HTTPException(404, "奖项不存在")
    db.delete(p)
    db.commit()
    return {"ok": True}
