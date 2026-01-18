"""
Schedule API Routes
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException

from app.services import ScheduleService
from app.schemas import FacilityResponse, ScheduleResponse

router = APIRouter()


@router.get("/facilities", response_model=List[FacilityResponse])
async def get_facilities():
    """
    시설 목록 조회

    Returns:
        시설명, 최신 월, 스케줄 개수 목록
    """
    facilities = ScheduleService.get_facilities()
    return facilities


@router.get("/schedules", response_model=List[dict])
async def get_schedules(
    facility: Optional[str] = Query(None, description="시설명 (예: 야탑유스센터)"),
    month: Optional[str] = Query(None, description="월 (예: 2026-01 또는 2026년 1월)")
):
    """
    스케줄 조회

    Args:
        facility: 시설명 필터 (옵션)
        month: 월 필터 (옵션)

    Returns:
        스케줄 목록
    """
    schedules = ScheduleService.get_schedules(facility=facility, month=month)
    return schedules


@router.get("/schedules/daily", response_model=List[dict])
async def get_daily_schedules(
    date: str = Query(..., description="날짜 (YYYY-MM-DD 형식, 예: 2026-01-18)")
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

    schedules = ScheduleService.get_daily_schedules(date)

    if not schedules:
        # 빈 결과는 정상 응답 (해당 날짜에 운영하는 시설이 없을 수 있음)
        return []

    return schedules


@router.get("/schedules/calendar")
async def get_calendar_schedules(
    year: int = Query(..., description="년도 (예: 2026)"),
    month: int = Query(..., ge=1, le=12, description="월 (1-12)")
):
    """
    달력용 스케줄 조회

    Args:
        year: 년도
        month: 월 (1-12)

    Returns:
        달력 데이터
    """
    calendar_data = ScheduleService.get_calendar_data(year=year, month=month)
    return calendar_data
