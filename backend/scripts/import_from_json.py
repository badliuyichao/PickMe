"""
从原桌面版 (D:/03-CODE/PickMe/data/) 导入数据到 PickMe Web SQLite。

用法: cd backend && python -m scripts.import_from_json
幂等: 跑过一次后生成 imported.flag, 跳过
"""
import json
import os
import sys
from pathlib import Path

# 允许作为模块运行
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal, init_db, DB_PATH
from app.models import Participant, Prize, Result

SOURCE_DIR = Path(r"D:/03-CODE/PickMe/data")
FLAG = Path(__file__).resolve().parent / "imported.flag"


def load_json(name):
    p = SOURCE_DIR / name
    if not p.exists():
        print(f"[skip] {p} not found")
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    if FLAG.exists():
        print(f"[skip] already imported, flag = {FLAG}")
        return 0

    if not SOURCE_DIR.exists():
        print(f"[err] source dir not found: {SOURCE_DIR}")
        return 1

    init_db()

    with SessionLocal() as db:
        # 1. Participants
        data = load_json("participants.json") or {}
        ps = data.get("participants", [])
        p_count = 0
        for p in ps:
            name = p.get("name", "").strip()
            if not name:
                continue
            db.add(Participant(name=name, department=p.get("department", "")))
            p_count += 1
        print(f"[import] participants: {p_count}")

        # 2. Prizes (保留原 id, 注意若与默认奖项冲突会失败)
        data = load_json("prizes.json") or {}
        ps = data.get("prizes", [])
        # 先清空默认的 3 个, 用原数据替代
        db.query(Prize).delete()
        pr_count = 0
        for p in ps:
            db.add(Prize(
                id=p.get("id"),
                name=p.get("name", "").strip(),
                count=int(p.get("count", 1)),
                drawn=int(p.get("drawn", 0)),
                color=p.get("color", "#FFD700"),
            ))
            pr_count += 1
        print(f"[import] prizes: {pr_count}")

        # 3. Results
        data = load_json("results.json") or {}
        rs = data.get("results", [])
        r_count = 0
        for r in rs:
            db.add(Result(
                prize_id=int(r.get("prize_id", 0)),
                prize_name=r.get("prize_name", ""),
                winner_id=int(r.get("winner_id", 0)),
                winner_name=r.get("winner_name", ""),
                timestamp=r.get("timestamp"),  # 字符串也能存, 取决于 SQLite 类型亲和
            ))
            r_count += 1
        print(f"[import] results: {r_count}")

        db.commit()

    FLAG.write_text(f"imported at {os.environ.get('USERNAME', '?')}\n", encoding="utf-8")
    print(f"[ok] done. db = {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
