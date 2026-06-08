# PickMe Web

一个**双击 exe 即可用**的抽奖系统，由原桌面版 [PickMe](../PickMe) 改造而来。

- 后端：FastAPI + SQLite + SQLAlchemy + sse-starlette（SSE 实时推送）
- 前端：原生 HTML/JS + Three.js（内联，不走 CDN）
- 打包：PyInstaller `--onefile` 跨平台

## 开发模式

```bash
cd backend
python -m pip install -r requirements.txt
python run.py
# 浏览器自动打开 http://127.0.0.1:8000
```

或手动启动：
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## 从原桌面版导入数据

```bash
cd backend
python -m scripts.import_from_json
```
会从 `D:/03-CODE/PickMe/data/*.json` 读取 participants / prizes / results，写入 SQLite。
幂等：执行过一次后生成 `imported.flag`，跳过。

## 打包为单 exe

```bash
cd backend
python -m pip install pyinstaller
# 一次性下载 three.min.js (如果 web/js/three.min.js 不存在)
python scripts/fetch_threejs.py
# 打包
pyinstaller --clean pickme.spec
# 产物: dist/PickMe.exe  (Windows)
```
跨平台：
- Windows: `dist/PickMe.exe`（~40MB）
- macOS:   `dist/PickMe`（在 macOS 上重新打包）
- Linux:   `dist/PickMe`（在目标 Linux 上重新打包，需 glibc ≥ 2.31 + libstdc++6）

## 端到端测试

```bash
cd backend
python -m tests.test_concurrent_draw
```
100 个协程同时抽奖，断言无重复中奖。

## 目录结构

```
backend/
├── app/
│   ├── main.py             FastAPI 入口 (lifespan + 路由 + StaticFiles)
│   ├── database.py         SQLAlchemy engine + WAL PRAGMA
│   ├── models.py           Participant / Prize / Result
│   ├── schemas.py          Pydantic 校验
│   ├── lottery_engine.py   asyncio.Lock 串行化的抽奖引擎
│   ├── sse_bus.py          SSE pub/sub
│   ├── static_loader.py    兼容 dev / _MEIPASS
│   └── routes/             participants / prizes / results / draw / sse
├── web/                    前端 (PyInstaller --add-data 打包)
│   ├── index.html
│   ├── css/
│   └── js/
│       ├── three.min.js    669KB, 本地
│       ├── three/
│       │   ├── background.js  Three.js 粒子背景
│       │   ├── firework.js     烟花粒子系统
│       │   ├── roller.js       Canvas 2D 姓名滚动
│       │   └── fx.js           场景主控
│       ├── api.js          fetch 封装
│       ├── sse.js          EventSource 客户端
│       └── tabs/           4 个 tab 模块 (lazy import)
├── scripts/
│   ├── import_from_json.py
│   └── fetch_threejs.py
├── data/                   SQLite 文件 (运行期生成)
├── tests/
│   └── test_concurrent_draw.py
├── pickme.spec
├── requirements.txt
└── run.py                  启动入口 (uvicorn + 自动开浏览器)
```

## API 速查

| Method | Path | 用途 |
|---|---|---|
| GET    | `/api/participants`           | 列出所有参与者 |
| POST   | `/api/participants`           | 添加一个 `{name, department}` |
| POST   | `/api/participants/batch`     | 批量导入 `{text: "a\nb\n...", department}` |
| DELETE | `/api/participants/{id}`      | 删除 |
| DELETE | `/api/participants`           | 清空 |
| GET    | `/api/prizes`                 | 列出奖项 |
| GET    | `/api/prizes/defaults`        | 6 预设颜色 |
| POST   | `/api/prizes`                 | 创建 `{name, count, color}` |
| PUT    | `/api/prizes/{id}`            | 更新 (任选字段) |
| DELETE | `/api/prizes/{id}`            | 删除 |
| GET    | `/api/results`                | 中奖结果 |
| DELETE | `/api/results`                | 清空 + 重置 drawn |
| POST   | `/api/draw`                   | 抽奖 `{prize_id}` |
| GET    | `/api/stream`                 | **SSE** 端点, 事件: `connected` / `draw_completed` / `reset` |

## SSE 事件

```
event: connected
data: {"ts": 1700000000.0}

event: draw_completed
data: {"result": {...}, "prize": {...}, "remaining_pool": 42}

event: reset
data: {"deleted": 10}
```

## 设计决策

- **SSE vs WebSocket**: 本场景服务端只推 3 类单向事件，SSE 自动重连 + 少一个依赖
- **SQLite + WAL**: 单进程 + WAL 模式，千人级活动够用；高并发改 Postgres 只换 `DATABASE_URL`
- **asyncio.Lock**: 抽奖用 Lock 串行化，保证 100 并发请求无重复 winner
- **SAVEPOINT 嵌套事务**: FastAPI Depends 的 session 已开 transaction，抽奖用 `begin_nested()` 避免冲突
- **前端 lazy import**: 4 个 tab 用 dynamic import 切到才加载
- **PyInstaller hiddenimports**: uvicorn / sse_starlette 动态加载的子模块必须显式列入
