"""
Schedule Repository Interface

스케줄 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.schedule.model import SwimSchedule


class ScheduleRepository(ABC):
    """스케줄 Repository 인터페이스"""

    @abstractmethod
    def find_schedules(
        self,
        facility_name: Optional[str] = None,
        valid_month: Optional[str] = None
    ) -> List[SwimSchedule]:
        """시설명/월 필터 스케줄 조회 (facility, sessions eager load)"""
        pass

    @abstractmethod
    def find_by_day_type_and_month(
        self, day_type: str, valid_month: str
    ) -> List[SwimSchedule]:
        """요일 타입 + 월별 스케줄 조회 (facility, sessions eager load)"""
        pass

    @abstractmethod
    def count_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> int:
        """시설 + 월별 스케줄 개수"""
        pass
