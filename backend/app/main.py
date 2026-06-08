"""
PickMe Web - FastAPI 入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.static_loader import static_dir
from app.database import init_db
from app.routes import participants, prizes, results, draw, sse


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="PickMe Web", version="1.0.0", lifespan=lifespan)

app.include_router(participants.router)
app.include_router(prizes.router)
app.include_router(results.router)
app.include_router(draw.router)
app.include_router(sse.router)


@app.get("/api/health")
async def health():
    return {"ok": True, "service": "pickme-web"}


# 静态资源 (前端 web/ 目录)
app.mount("/", StaticFiles(directory=str(static_dir()), html=True), name="web")
