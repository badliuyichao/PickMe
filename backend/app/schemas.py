"""
Pydantic 校验模型
"""
from typing import List, Optional
from pydantic import BaseModel, Field



# ===== Participant =====
class ParticipantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    department: str = Field("", max_length=64)


class ParticipantBatchCreate(BaseModel):
    """textarea 批量导入：每行一个姓名"""
    text: str = Field(..., min_length=1)
    department: str = Field("", max_length=64)


# ===== Prize =====
class PrizeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    count: int = Field(..., ge=1, le=10000)
    color: str = Field("#FFD700", pattern=r"^#[0-9A-Fa-f]{6}$")


class PrizeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    count: Optional[int] = Field(None, ge=1, le=10000)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


# ===== Draw =====
class DrawRequest(BaseModel):
    prize_id: int = Field(..., ge=1)
