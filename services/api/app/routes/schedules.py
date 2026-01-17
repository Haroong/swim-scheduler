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
