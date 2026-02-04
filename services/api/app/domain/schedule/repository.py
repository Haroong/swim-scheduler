"""
Schedule Repository Interface

스케줄 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.schedule.model import SwimSchedule, SwimSession


class ScheduleRepository(ABC):
    """스케줄 Repository 인터페이스"""

    @abstractmethod
    def find_by_id(self, schedule_id: int) -> Optional[SwimSchedule]:
        """ID로 스케줄 조회"""
        pass

    @abstractmethod
    def find_by_facility_id(self, facility_id: int) -> List[SwimSchedule]:
        """시설 ID로 스케줄 목록 조회"""
        pass

    @abstractmethod
    def find_by_month(self, valid_month: str) -> List[SwimSchedule]:
        """월별 스케줄 조회"""
        pass

    @abstractmethod
    def find_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> List[SwimSchedule]:
        """시설 + 월별 스케줄 조회"""
        pass

    @abstractmethod
    def find_by_day_type_and_month(
        self, day_type: str, valid_month: str
    ) -> List[SwimSchedule]:
        """요일 타입 + 월별 스케줄 조회"""
        pass

    @abstractmethod
    def save(self, schedule: SwimSchedule) -> SwimSchedule:
        """스케줄 저장"""
        pass

    @abstractmethod
    def delete(self, schedule: SwimSchedule) -> None:
        """스케줄 삭제"""
        pass


class SessionRepository(ABC):
    """세션 Repository 인터페이스"""

    @abstractmethod
    def find_by_schedule_id(self, schedule_id: int) -> List[SwimSession]:
        """스케줄 ID로 세션 목록 조회"""
        pass

    @abstractmethod
    def save(self, session: SwimSession) -> SwimSession:
        """세션 저장"""
        pass

    @abstractmethod
    def delete(self, session: SwimSession) -> None:
        """세션 삭제"""
        pass
