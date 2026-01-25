"""
Database Session Management

SQLAlchemy 세션 관리 및 FastAPI 의존성 주입
"""
import sys
from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Parser 경로 추가
parser_path = Path(__file__).parent.parent.parent.parent.parent / "parser"
sys.path.insert(0, str(parser_path))

from infrastructure.config import settings

# SQLAlchemy 엔진 생성
SQLALCHEMY_DATABASE_URL = settings.db_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 연결 유효성 체크
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_POOL_MAX_OVERFLOW,
    pool_recycle=3600,  # 1시간마다 연결 재생성
    echo=False,  # SQL 로깅 (개발 시에만 True)
)

# 세션 팩토리
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI 의존성 주입용 DB 세션

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "get_db"]
