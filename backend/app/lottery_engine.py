"""
抽奖引擎

设计要点:
1. 进程内单例（每个 FastAPI app 一个），绑定一个 asyncio.Lock 串行化所有抽奖请求
2. 关键操作 (读 prize / 查 winners / 抽 winner / 写 result / 累加 drawn) 在一个事务内完成
3. SQLite 不支持 SELECT FOR UPDATE 写锁，但有 asyncio.Lock + BEGIN IMMEDIATE 等价语义
4. 抽完返回 Result 对象，路由层把它转成 dict + 通过 SSE 广播
"""
import asyncio
import random
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Participant, Prize, Result


class LotteryEngine:
    def __init__(self):
        self._lock = asyncio.Lock()

    async def draw(self, prize_id: int, db: Session) -> Optional[dict]:
        """
        并发安全地执行一次抽奖。
        返回: {"result": Result, "prize": Prize, "remaining_pool": int} 或 None (无法抽)

        注意: FastAPI Depends(get_db) 已经在 session 上开了 transaction (autobegin 模式)。
        我们用 SAVEPOINT 嵌套事务, 退出 with 块时自动 commit。
        """
        async with self._lock:
            with db.begin_nested():
                prize = db.get(Prize, prize_id)
                if not prize:
                    return None
                if prize.drawn >= prize.count:
                    return None

                # 查所有已中奖者 ID
                winner_ids = {r.winner_id for r in db.query(Result.winner_id).all()}

                # 排除已中奖者
                pool = (
                    db.query(Participant)
                    .filter(~Participant.id.in_(winner_ids))
                    .all()
                )
                if not pool:
                    return None

                winner = random.choice(pool)
                result = Result(
                    prize_id=prize.id,
                    prize_name=prize.name,
                    winner_id=winner.id,
                    winner_name=winner.name,
                )
                db.add(result)
                prize.drawn += 1

            # SAVEPOINT 已释放, 主动 commit 让外层 transaction 落地
            db.commit()

            # 再查剩余奖池大小用于 SSE 推送
            winner_ids = {r.winner_id for r in db.query(Result.winner_id).all()}
            remaining_pool = db.query(Participant).filter(
                ~Participant.id.in_(winner_ids)
            ).count()

            return {
                "result": result.to_dict(),
                "prize": prize.to_dict(),
                "remaining_pool": remaining_pool,
            }

    def can_draw(self, prize_id: int, db: Session) -> tuple[bool, str]:
        """同步检查 (不占 lock) - 仅用于路由的预检"""
        prize = db.get(Prize, prize_id)
        if not prize:
            return False, "奖项不存在"
        if prize.drawn >= prize.count:
            return False, "该奖项已抽取完毕"
        winner_ids = {r.winner_id for r in db.query(Result.winner_id).all()}
        pool = db.query(Participant).filter(~Participant.id.in_(winner_ids)).count()
        if pool == 0:
            return False, "没有剩余参与者"
        return True, "可以抽奖"


# 全局单例（在 main.py 的 lifespan 里实例化）
engine: Optional[LotteryEngine] = None


def get_engine() -> LotteryEngine:
    global engine
    if engine is None:
        engine = LotteryEngine()
    return engine
