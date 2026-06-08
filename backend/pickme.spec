# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for PickMe Web.
用法: pyinstaller pickme.spec
"""
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hiddenimports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "fastapi.staticfiles",
    "starlette",
    "starlette.staticfiles",
    "sse_starlette",
    "sse_starlette.sse",
    "sqlalchemy.dialects.sqlite",
    "anyio",
    "anyio._backends._asyncio",
    "sniffio",
    "h11",
]
hiddenimports += collect_submodules("uvicorn")
hiddenimports += collect_submodules("sse_starlette")

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('web', 'web'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'customtkinter', 'pygame', 'PIL',
        'matplotlib', 'numpy', 'pandas', 'scipy',
        'pytest', 'setuptools', 'pip', 'wheel',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    [],
    name='PickMe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # 关闭 UPX 避免误报
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,        # 控制台可见 (方便看日志)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,           # 如有 icon.ico 可填
)
