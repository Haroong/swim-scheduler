"""
Schedule API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from fastapi_cache.decorator import cache

from app.services import ScheduleService
from app.schemas import FacilityResponse, ScheduleResponse
from app.database import get_db
from app.config.settings import settings
from app.config.cache import cache_key_builder

router = APIRouter()


@router.get("/facilities", response_model=List[FacilityResponse])
@cache(expire=settings.CACHE_TTL_FACILITIES, key_builder=cache_key_builder)
async def get_facilities(request: Request, db: Session = Depends(get_db)):
    """
    시설 목록 조회

    Returns:
        시설명, 최신 월, 스케줄 개수 목록
    """
    facilities = ScheduleService.get_facilities(db)
    return facilities


@router.get("/schedules", response_model=List[dict])
@cache(expire=settings.CACHE_TTL_SCHEDULES, key_builder=cache_key_builder)
async def get_schedules(
    request: Request,
    facility: Optional[str] = Query(None, description="시설명 (예: 야탑유스센터)"),
    month: Optional[str] = Query(None, description="월 (예: 2026-01 또는 2026년 1월)"),
    db: Session = Depends(get_db)
):
    """
    스케줄 조회

    Args:
        facility: 시설명 필터 (옵션)
        month: 월 필터 (옵션)

    Returns:
        스케줄 목록
    """
    schedules = ScheduleService.get_schedules(db, facility=facility, month=month)
    return schedules


@router.get("/schedules/daily", response_model=List[dict])
@cache(expire=settings.CACHE_TTL_DAILY, key_builder=cache_key_builder)
async def get_daily_schedules(
    request: Request,
    date: str = Query(..., description="날짜 (YYYY-MM-DD 형식, 예: 2026-01-18)"),
    db: Session = Depends(get_db)
):
    """
    특정 날짜의 자유수영 스케줄 조회

    Args:
        date: 날짜 (YYYY-MM-DD)

    Returns:
        해당 날짜에 운영하는 모든 시설의 스케줄 목록

    Example:
        /api/schedules/daily?date=2026-01-18
    """
    # 날짜 형식 간단 검증
    if len(date) != 10 or date.count('-') != 2:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.")

    schedules = ScheduleService.get_daily_schedules(db, date)

    if not schedules:
        # 빈 결과는 정상 응답 (해당 날짜에 운영하는 시설이 없을 수 있음)
        return []

    return schedules


@router.get("/schedules/calendar")
@cache(expire=settings.CACHE_TTL_CALENDAR, key_builder=cache_key_builder)
async def get_calendar_schedules(
    request: Request,
    year: int = Query(..., description="년도 (예: 2026)"),
    month: int = Query(..., ge=1, le=12, description="월 (1-12)"),
    db: Session = Depends(get_db)
):
    """
    달력용 스케줄 조회

    Args:
        year: 년도
        month: 월 (1-12)

    Returns:
        달력 데이터
    """
    calendar_data = ScheduleService.get_calendar_data(db, year=year, month=month)
    return calendar_data
