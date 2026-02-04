"""
Schedule Presentation DTOs (Response Schemas)

API 응답을 위한 Pydantic 스키마
"""
from typing import List, Optional
from pydantic import BaseModel


# ==================== Facility ====================

class FacilityResponse(BaseModel):
    """시설 응답 스키마"""
    facility_id: int
    facility_name: str
    latest_month: Optional[str] = None
    schedule_count: int


# ==================== Schedule ====================

class SessionSchema(BaseModel):
    """수영 세션 스키마"""
    session_name: str
    start_time: str
    end_time: str
    capacity: Optional[int] = None
    lanes: Optional[int] = None
    applicable_days: Optional[str] = None  # 적용 요일 (NULL=전체, "수"=수요일만)


class ScheduleDetailSchema(BaseModel):
    """요일별 스케줄 스키마"""
    day_type: str  # "평일", "토요일", "일요일"
    season: str  # "하절기", "동절기", ""
    season_months: str = ""  # "3~10월", "11~2월", ""
    sessions: List[SessionSchema]


class FeeSchema(BaseModel):
    """이용료 스키마"""
    category: str
    price: int
    note: str


class ScheduleResponse(BaseModel):
    """스케줄 응답 스키마"""
    id: int
    facility_name: str
    valid_month: str
    schedules: List[ScheduleDetailSchema]
    fees: List[FeeSchema]
    notes: List[str]
    source_url: Optional[str] = None
    created_at: str

    class Config:
        from_attributes = True


# ==================== Calendar ====================

class CalendarDayResponse(BaseModel):
    """달력용 일별 응답 스키마"""
    date: str  # "2026-01-15"
    facilities: List[str]  # 해당 날짜에 운영하는 시설 목록
    sessions_count: int  # 전체 세션 수
