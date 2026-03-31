# -*- coding: utf-8 -*-
"""
数据存储管理模块
"""
import json
import os
from typing import List, Dict, Any


class DataManager:
    """数据管理类"""

    def __init__(self, participants_file: str, prizes_file: str, results_file: str):
        self.participants_file = participants_file
        self.prizes_file = prizes_file
        self.results_file = results_file
        self._ensure_data_files()

    def _ensure_data_files(self):
        """确保数据文件存在"""
        # 确保data目录存在
        os.makedirs(os.path.dirname(self.participants_file), exist_ok=True)

        if not os.path.exists(self.participants_file):
            self._write_json(self.participants_file, {"participants": []})

        if not os.path.exists(self.prizes_file):
            from config import DEFAULT_PRIZES
            self._write_json(self.prizes_file, {"prizes": DEFAULT_PRIZES})

        if not os.path.exists(self.results_file):
            self._write_json(self.results_file, {"results": []})

    def _read_json(self, file_path: str) -> Dict:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取文件失败 {file_path}: {e}")
            return {}

    def _write_json(self, file_path: str, data: Dict):
        """写入JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入文件失败 {file_path}: {e}")

    # ==================== 参与者管理 ====================

    def get_participants(self) -> List[Dict]:
        """获取所有参与者"""
        data = self._read_json(self.participants_file)
        return data.get("participants", [])

    def add_participant(self, name: str, department: str = "") -> bool:
        """添加参与者"""
        participants = self.get_participants()
        new_id = max([p.get("id", 0) for p in participants], default=0) + 1
        participants.append({
            "id": new_id,
            "name": name,
            "department": department
        })
        self._write_json(self.participants_file, {"participants": participants})
        return True

    def add_participants_batch(self, names: List[str]) -> int:
        """批量添加参与者，返回成功添加的数量"""
        participants = self.get_participants()
        start_id = max([p.get("id", 0) for p in participants], default=0) + 1
        count = 0
        for i, name in enumerate(names):
            if name.strip():
                participants.append({
                    "id": start_id + i,
                    "name": name.strip(),
                    "department": ""
                })
                count += 1
        self._write_json(self.participants_file, {"participants": participants})
        return count

    def delete_participant(self, participant_id: int) -> bool:
        """删除参与者"""
        participants = self.get_participants()
        participants = [p for p in participants if p.get("id") != participant_id]
        self._write_json(self.participants_file, {"participants": participants})
        return True

    def clear_participants(self) -> bool:
        """清空所有参与者"""
        self._write_json(self.participants_file, {"participants": []})
        return True

    # ==================== 奖项管理 ====================

    def get_prizes(self) -> List[Dict]:
        """获取所有奖项"""
        data = self._read_json(self.prizes_file)
        return data.get("prizes", [])

    def add_prize(self, name: str, count: int, color: str = "#FFD700") -> bool:
        """添加奖项"""
        prizes = self.get_prizes()
        new_id = max([p.get("id", 0) for p in prizes], default=0) + 1
        prizes.append({
            "id": new_id,
            "name": name,
            "count": count,
            "drawn": 0,
            "color": color
        })
        self._write_json(self.prizes_file, {"prizes": prizes})
        return True

    def update_prize(self, prize_id: int, name: str = None, count: int = None, color: str = None) -> bool:
        """更新奖项"""
        prizes = self.get_prizes()
        for prize in prizes:
            if prize.get("id") == prize_id:
                if name is not None:
                    prize["name"] = name
                if count is not None:
                    prize["count"] = count
                if color is not None:
                    prize["color"] = color
                break
        self._write_json(self.prizes_file, {"prizes": prizes})
        return True

    def delete_prize(self, prize_id: int) -> bool:
        """删除奖项"""
        prizes = self.get_prizes()
        prizes = [p for p in prizes if p.get("id") != prize_id]
        self._write_json(self.prizes_file, {"prizes": prizes})
        return True

    # ==================== 结果管理 ====================

    def get_results(self) -> List[Dict]:
        """获取所有中奖结果"""
        data = self._read_json(self.results_file)
        return data.get("results", [])

    def add_result(self, prize_id: int, prize_name: str, winner_id: int, winner_name: str) -> bool:
        """添加中奖结果"""
        results = self.get_results()
        from datetime import datetime
        results.append({
            "prize_id": prize_id,
            "prize_name": prize_name,
            "winner_id": winner_id,
            "winner_name": winner_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        self._write_json(self.results_file, {"results": results})

        # 更新奖项的已抽取数量
        prizes = self.get_prizes()
        for prize in prizes:
            if prize.get("id") == prize_id:
                prize["drawn"] = prize.get("drawn", 0) + 1
                break
        self._write_json(self.prizes_file, {"prizes": prizes})
        return True

    def get_winner_ids(self) -> List[int]:
        """获取所有已中奖的人员ID列表"""
        results = self.get_results()
        return [r.get("winner_id") for r in results]

    def clear_results(self) -> bool:
        """清空所有结果"""
        self._write_json(self.results_file, {"results": []})
        # 重置所有奖项的已抽取数量
        prizes = self.get_prizes()
        for prize in prizes:
            prize["drawn"] = 0
        self._write_json(self.prizes_file, {"prizes": prizes})
        return True

    # ==================== 导出功能 ====================

    def export_to_txt(self, file_path: str) -> bool:
        """导出参与者名单到文本文件"""
        participants = self.get_participants()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for p in participants:
                    f.write(f"{p['name']}\n")
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False

    def export_results_to_txt(self, file_path: str) -> bool:
        """导出中奖结果到文本文件"""
        results = self.get_results()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for r in results:
                    f.write(f"{r['prize_name']}: {r['winner_name']} ({r['timestamp']})\n")
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False