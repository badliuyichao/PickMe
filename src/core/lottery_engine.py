# -*- coding: utf-8 -*-
"""
抽奖引擎核心模块
"""
import random
from typing import List, Dict, Optional
from src.utils.data_manager import DataManager


class LotteryEngine:
    """抽奖引擎"""

    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.current_prize = None
        self.remaining_participants = []

    def update_remaining_participants(self):
        """更新剩余参与者列表（排除已中奖者）"""
        all_participants = self.data_manager.get_participants()
        winner_ids = self.data_manager.get_winner_ids()
        self.remaining_participants = [
            p for p in all_participants
            if p.get("id") not in winner_ids
        ]

    def get_remaining_count(self) -> int:
        """获取剩余参与者数量"""
        self.update_remaining_participants()
        return len(self.remaining_participants)

    def set_current_prize(self, prize_id: int) -> Dict:
        """设置当前奖项"""
        prizes = self.data_manager.get_prizes()
        for prize in prizes:
            if prize.get("id") == prize_id:
                remaining = prize["count"] - prize.get("drawn", 0)
                if remaining > 0:
                    self.current_prize = prize
                    return {"success": True, "prize": prize}
                else:
                    return {"success": False, "message": "该奖项已抽取完毕"}
        return {"success": False, "message": "奖项不存在"}

    def draw(self) -> Optional[Dict]:
        """
        执行抽奖
        返回: 中奖者信息字典，如果无法抽取则返回None
        """
        if not self.current_prize:
            return None

        # 检查是否还有剩余名额
        remaining_count = self.current_prize["count"] - self.current_prize.get("drawn", 0)
        if remaining_count <= 0:
            return None

        # 更新剩余参与者
        self.update_remaining_participants()

        if len(self.remaining_participants) == 0:
            return None

        # 随机抽取
        winner = random.choice(self.remaining_participants)

        # 记录结果
        self.data_manager.add_result(
            prize_id=self.current_prize["id"],
            prize_name=self.current_prize["name"],
            winner_id=winner["id"],
            winner_name=winner["name"]
        )

        # 从剩余列表中移除
        self.remaining_participants.remove(winner)

        return {
            "winner": winner,
            "prize": self.current_prize
        }

    def can_draw(self) -> tuple:
        """
        检查是否可以继续抽奖
        返回: (can_draw: bool, message: str)
        """
        if not self.current_prize:
            return False, "请先选择奖项"

        remaining_count = self.current_prize["count"] - self.current_prize.get("drawn", 0)
        if remaining_count <= 0:
            return False, "该奖项已抽取完毕"

        self.update_remaining_participants()
        if len(self.remaining_participants) == 0:
            return False, "没有剩余参与者"

        return True, "可以抽奖"

    def get_random_names_for_animation(self, count: int = 50) -> List[str]:
        """
        获取用于动画展示的随机姓名列表
        参数:
            count: 需要的名字数量
        返回:
            随机姓名列表
        """
        all_participants = self.data_manager.get_participants()
        if len(all_participants) == 0:
            return []

        names = [p["name"] for p in all_participants]
        # 随机打乱并重复，确保有足够数量
        random.shuffle(names)
        while len(names) < count:
            names.extend(names[:min(count - len(names), len(names))])

        return names[:count]