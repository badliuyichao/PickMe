"""
PickMe Web 启动入口

功能:
1. 初始化数据库
2. 探测空闲端口
3. 启动 uvicorn
4. 自动打开浏览器到 http://127.0.0.1:<port>

被 PyInstaller 打包时, 此文件是入口。
"""
import asyncio
import socket
import sys
import webbrowser
from pathlib import Path

import uvicorn

# 确保本地 app 包可被找到
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

from app.main import app  # noqa: E402
from app.database import init_db  # noqa: E402


def pick_free_port(start: int = 8000, end: int = 8010) -> int:
    for p in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError(f"No free port in {start}-{end}")


async def main():
    init_db()
    port = pick_free_port()
    url = f"http://127.0.0.1:{port}"
    print(f"\n  PickMe Web  ->  {url}\n")
    # 异步开浏览器, 不阻塞 server
    asyncio.get_event_loop().run_in_executor(None, lambda: webbrowser.open(url))

    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="info",
        access_log=False,  # 关掉 access log, 控制台更安静
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[PickMe] bye")
