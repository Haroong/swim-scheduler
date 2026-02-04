"""
Swim Scheduler API
FastAPI 기반 수영장 스케줄 API 서버
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 로깅 설정 초기화 (가장 먼저 import)
from app.config import logging_config

from app.routes import schedules
from app.models.base import Base
from app.database.session import engine
from app.config.cache import init_cache, close_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작/종료 시 실행되는 이벤트
    - 시작 시: 테이블 자동 생성, Redis 캐시 초기화
    - 종료 시: Redis 연결 종료
    """
    # Startup: 테이블 자동 생성 (Spring JPA의 ddl-auto: update와 유사)
    # 모든 모델 import하여 Base.metadata에 등록
    from app.models import facility, schedule, notice, fee
    Base.metadata.create_all(bind=engine)

    # Redis 캐시 초기화
    await init_cache()

    yield

    # Shutdown: Redis 연결 종료
    await close_cache()


app = FastAPI(
    title="Swim Scheduler API",
    description="성남시 수영장 자유수영 스케줄 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (React 연동)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",  # Vite 기본 포트들
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(schedules.router, prefix="/api", tags=["schedules"])


@app.get("/")
async def root():
    """API 루트"""
    return {
        "message": "Swim Scheduler API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy"}
