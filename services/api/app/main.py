"""
Swim Scheduler API
FastAPI 기반 수영장 스케줄 API 서버
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import schedules

app = FastAPI(
    title="Swim Scheduler API",
    description="성남시 수영장 자유수영 스케줄 API",
    version="1.0.0"
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
