"""
一次性脚本: 从 CDN 下载 three.min.js 到 web/js/, 让 PyInstaller --add-data 把它打包进 exe
不依赖外网运行时 (设计目标: 独立部署)
"""
import urllib.request
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "web" / "js" / "three.min.js"
URL = "https://unpkg.com/three@0.160.0/build/three.min.js"


def main():
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    if TARGET.exists() and TARGET.stat().st_size > 100_000:
        print(f"[skip] {TARGET} already exists ({TARGET.stat().st_size} bytes)")
        return
    print(f"[fetch] {URL}")
    urllib.request.urlretrieve(URL, TARGET)
    print(f"[ok] saved to {TARGET} ({TARGET.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
