"""
Schedule API Controller (Routes)

스케줄 관련 API 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException, Depends, Request
from fastapi_cache.decorator import cache

from app.application import ScheduleService
from app.presentation.schedule.response import FacilityResponse
from app.infrastructure.persistence.dependencies import get_schedule_service
from app.shared.config import settings
from app.infrastructure.cache import cache_key_builder

router = APIRouter()


@router.get("/facilities", response_model=List[FacilityResponse])
@cache(expire=settings.CACHE_TTL_FACILITIES, key_builder=cache_key_builder)
async def get_facilities(request: Request, service: ScheduleService = Depends(get_schedule_service)):
    """시설 목록 조회"""
    return service.get_facilities()


@router.get("/schedules", response_model=List[dict])
@cache(expire=settings.CACHE_TTL_SCHEDULES, key_builder=cache_key_builder)
async def get_schedules(
    request: Request,
    facility: Optional[str] = Query(None, description="시설명 (예: 야탑유스센터)"),
    month: Optional[str] = Query(None, description="월 (예: 2026-01 또는 2026년 1월)"),
    service: ScheduleService = Depends(get_schedule_service),
):
    """스케줄 조회"""
    return service.get_schedules(facility=facility, month=month)


@router.get("/schedules/daily", response_model=List[dict])
@cache(expire=settings.CACHE_TTL_DAILY, key_builder=cache_key_builder)
async def get_daily_schedules(
    request: Request,
    date: str = Query(..., description="날짜 (YYYY-MM-DD 형식, 예: 2026-01-18)"),
    service: ScheduleService = Depends(get_schedule_service),
):
    """특정 날짜의 자유수영 스케줄 조회"""
    if len(date) != 10 or date.count('-') != 2:
        raise HTTPException(status_code=400, detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용하세요.")

    schedules = service.get_daily_schedules(date)

    if not schedules:
        return []

    return schedules


@router.get("/schedules/calendar")
@cache(expire=settings.CACHE_TTL_CALENDAR, key_builder=cache_key_builder)
async def get_calendar_schedules(
    request: Request,
    year: int = Query(..., description="년도 (예: 2026)"),
    month: int = Query(..., ge=1, le=12, description="월 (1-12)"),
    service: ScheduleService = Depends(get_schedule_service),
):
    """달력용 스케줄 조회"""
    return service.get_calendar_data(year=year, month=month)
