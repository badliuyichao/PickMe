"""
SQLAlchemy ORM 模型

字段语义与原桌面版 data_manager.py 保持一致：
- Participant: name, department
- Prize: name, count, drawn, color
- Result: prize_id, prize_name (反范式), winner_id, winner_name (反范式), timestamp
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from app.database import Base


class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, index=True)
    department = Column(String(64), default="", nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "department": self.department}


class Prize(Base):
    __tablename__ = "prizes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    count = Column(Integer, nullable=False, default=1)
    drawn = Column(Integer, nullable=False, default=0)
    color = Column(String(16), default="#FFD700", nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "count": self.count,
            "drawn": self.drawn,
            "color": self.color,
        }


class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    prize_id = Column(Integer, ForeignKey("prizes.id"), nullable=False)
    prize_name = Column(String(64), nullable=False)
    winner_id = Column(Integer, ForeignKey("participants.id"), nullable=False)
    winner_name = Column(String(64), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_results_prize", "prize_id"),
        Index("ix_results_winner", "winner_id"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "prize_id": self.prize_id,
            "prize_name": self.prize_name,
            "winner_id": self.winner_id,
            "winner_name": self.winner_name,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }
