"""
数据库引擎与会话工厂
"""
import os
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# 测试时通过环境变量 PICKME_TEST_DB 指定临时 DB
_TEST_DB = os.environ.get("PICKME_TEST_DB")
if _TEST_DB:
    DB_PATH = Path(_TEST_DB)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
else:
    DATA_DIR = Path(__file__).resolve().parent.parent / "data"
    DATA_DIR.mkdir(exist_ok=True)
    DB_PATH = DATA_DIR / "pickme.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _):
    """启用 WAL 模式 + 外键约束，提高并发读性能。"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db():
    """建表（首次启动调用）"""
    from app import models  # noqa: F401  确保模型被注册
    Base.metadata.create_all(bind=engine)

    # 首次启动：填充默认奖项（仅当 prizes 表为空时）
    from app.models import Prize
    with SessionLocal() as db:
        if db.query(Prize).count() == 0:
            defaults = [
                Prize(name="特等奖", count=1, drawn=0, color="#FFD700"),
                Prize(name="一等奖", count=3, drawn=0, color="#C0C0C0"),
                Prize(name="二等奖", count=5, drawn=0, color="#CD7F32"),
            ]
            db.add_all(defaults)
            db.commit()


def get_db() -> Session:
    """FastAPI 依赖：每个请求一个 Session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
