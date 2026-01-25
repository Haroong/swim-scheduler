"""
Facility related schemas
"""
from typing import Optional
from pydantic import BaseModel


class FacilityResponse(BaseModel):
    """시설 응답 스키마"""
    facility_id: int
    facility_name: str
    latest_month: Optional[str] = None
    schedule_count: int
