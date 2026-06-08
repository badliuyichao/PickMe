"""
并发抽奖单测: 100 个协程同时 POST /api/draw, 断言无重复 winner_id。

运行: cd backend && python -m tests.test_concurrent_draw
"""
import asyncio
import httpx
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Windows GBK console -> 强制 UTF-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# 用临时目录避免污染真实数据
TMP = Path(tempfile.mkdtemp(prefix="pickme_test_"))
TEST_DB = TMP / "pickme.db"

# 在 import 之前重写 DB_PATH
os.environ["PICKME_TEST_DB"] = str(TEST_DB)


async def setup_data(client: httpx.AsyncClient, n_participants: int = 50, prize_count: int = 100):
    """灌入 50 个参与者 + 1 个可抽 100 次的奖项"""
    r = await client.delete("/api/participants")
    print(f"  清空参与者: {r.status_code} {r.text[:100]}")
    names = "\n".join(f"测试员{i:03d}" for i in range(n_participants))
    r = await client.post("/api/participants/batch",
                          json={"text": names, "department": "QA"})
    print(f"  批量导入: {r.status_code} {r.text[:200]}")
    assert r.status_code == 200, f"批量导入失败: {r.status_code} {r.text}"
    assert r.json()["added"] == n_participants

    # 清空奖项再创建 1 个
    prizes = (await client.get("/api/prizes")).json()
    for p in prizes:
        await client.delete(f"/api/prizes/{p['id']}")
    r = await client.post("/api/prizes",
                          json={"name": "测试大奖", "count": prize_count, "color": "#FFD700"})
    assert r.status_code == 200
    return r.json()["id"]


async def main():
    # 启动 server
    import subprocess
    server_log = TMP / "server.log"
    log_f = open(server_log, "w", encoding="utf-8")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", "8765", "--log-level", "info"],
        cwd=Path(__file__).resolve().parent.parent,
        env={**os.environ, "PICKME_TEST_DB": str(TEST_DB)},
        stdout=log_f,
        stderr=subprocess.STDOUT,
    )
    try:
        # 等 server 起来
        async with httpx.AsyncClient(timeout=10) as probe:
            for _ in range(30):
                try:
                    r = await probe.get("http://127.0.0.1:8765/api/health")
                    if r.status_code == 200:
                        break
                except Exception:
                    pass
                await asyncio.sleep(0.2)
            else:
                raise RuntimeError("server failed to start")

            # 真实 base url
            base = "http://127.0.0.1:8765"
            client = httpx.AsyncClient(base_url=base, timeout=10)
            try:
                # 灌数据
                n = 50
                prize_id = await setup_data(client, n_participants=n, prize_count=100)
                print(f"[OK] seed {n} participants, prize_id={prize_id}")

                # 100 个并发抽奖
                async def do_draw(i):
                    return await client.post("/api/draw", json={"prize_id": prize_id})

                tasks = [do_draw(i) for i in range(100)]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                ok = [r for r in responses if not isinstance(r, Exception) and r.status_code == 200]
                errs = [r for r in responses if isinstance(r, Exception) or r.status_code != 200]
                print(f"  success: {len(ok)} / 100, fail/exception: {len(errs)}")
                for e in errs[:3]:
                    print(f"  - {e}")

                # 收集 winner_id, 断言无重复
                winner_ids = [r.json()["result"]["winner_id"] for r in ok]
                assert len(winner_ids) == 50, f"expected 50 successes, got {len(winner_ids)} (50-participant cap)"
                assert len(set(winner_ids)) == len(winner_ids), "duplicate winner_id detected!"
                print(f"[OK] 50 unique winners, no duplicates")

                # 第 51 次应该 409
                r = await client.post("/api/draw", json={"prize_id": prize_id})
                assert r.status_code == 409, f"expected 409, got {r.status_code}"
                print(f"[OK] 51st request -> 409: {r.json()['detail']}")

                # 中奖名单应有 50 条
                results = (await client.get("/api/results")).json()
                assert len(results) == 50
                # prize.drawn 应为 50
                prizes = (await client.get("/api/prizes")).json()
                p = next(x for x in prizes if x["id"] == prize_id)
                assert p["drawn"] == 50
                print(f"[OK] DB consistent: results=50, drawn=50")

                print("\nAll tests passed!")
            finally:
                await client.aclose()
    finally:
        # 输出 server 日志 (调试用)
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
        log_f.close()
        try:
            log_text = server_log.read_text(encoding="utf-8", errors="replace")
            print("\n--- SERVER LOG ---")
            print(log_text[-3000:])
        except Exception:
            pass
        shutil.rmtree(TMP, ignore_errors=True)


if __name__ == "__main__":
    asyncio.run(main())
