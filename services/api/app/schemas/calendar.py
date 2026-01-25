"""
Calendar view related schemas
"""
from typing import List
from pydantic import BaseModel


class CalendarDayResponse(BaseModel):
    """달력용 일별 응답 스키마"""
    date: str  # "2026-01-15"
    facilities: List[str]  # 해당 날짜에 운영하는 시설 목록
    sessions_count: int  # 전체 세션 수
