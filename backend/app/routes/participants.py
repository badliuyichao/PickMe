"""
参与者管理 REST API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Participant
from app.schemas import ParticipantCreate, ParticipantBatchCreate

router = APIRouter(prefix="/api/participants", tags=["participants"])


@router.get("")
def list_participants(db: Session = Depends(get_db)) -> List[dict]:
    rows = db.query(Participant).order_by(Participant.id).all()
    return [p.to_dict() for p in rows]


@router.post("")
def create_participant(payload: ParticipantCreate, db: Session = Depends(get_db)) -> dict:
    p = Participant(name=payload.name.strip(), department=payload.department.strip())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p.to_dict()


@router.post("/batch")
def create_participants_batch(payload: ParticipantBatchCreate, db: Session = Depends(get_db)) -> dict:
    """批量导入：textarea 一行一个姓名（支持 \\n / \\r\\n）"""
    added = 0
    for raw in payload.text.splitlines():
        name = raw.strip()
        if not name:
            continue
        db.add(Participant(name=name, department=payload.department.strip()))
        added += 1
    db.commit()
    return {"added": added}


@router.delete("/{participant_id}")
def delete_participant(participant_id: int, db: Session = Depends(get_db)) -> dict:
    p = db.get(Participant, participant_id)
    if not p:
        raise HTTPException(404, "参与者不存在")
    db.delete(p)
    db.commit()
    return {"ok": True}


@router.delete("")
def clear_participants(db: Session = Depends(get_db)) -> dict:
    """清空所有参与者"""
    deleted = db.query(Participant).delete()
    db.commit()
    return {"deleted": deleted}
