"""
定位前端静态资源目录，同时兼容 dev (uvicorn) 和 PyInstaller --onefile 模式。

dev 模式:    backend/web/  (相对于本文件)
打包模式:    _MEIPASS/web/  (PyInstaller 临时解压目录)
"""
import sys
from pathlib import Path


def static_dir() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        base = Path(meipass)
    else:
        # app/static_loader.py → backend/
        base = Path(__file__).resolve().parent.parent
    target = base / "web"
    if not target.exists():
        raise FileNotFoundError(f"前端目录不存在: {target}")
    return target
