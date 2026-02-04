"""
Closure Repository Interface

휴무일 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date

from app.domain.closure.model import FacilityClosure


class ClosureRepository(ABC):
    """휴무일 Repository 인터페이스"""

    @abstractmethod
    def find_by_id(self, closure_id: int) -> Optional[FacilityClosure]:
        """ID로 휴무일 조회"""
        pass

    @abstractmethod
    def find_by_facility_id(self, facility_id: int) -> List[FacilityClosure]:
        """시설 ID로 휴무일 목록 조회"""
        pass

    @abstractmethod
    def find_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> List[FacilityClosure]:
        """시설 + 월별 휴무일 조회"""
        pass

    @abstractmethod
    def find_by_date(
        self, facility_id: int, closure_date: date
    ) -> Optional[FacilityClosure]:
        """시설 + 특정 날짜 휴무일 조회"""
        pass

    @abstractmethod
    def save(self, closure: FacilityClosure) -> FacilityClosure:
        """휴무일 저장"""
        pass

    @abstractmethod
    def delete(self, closure: FacilityClosure) -> None:
        """휴무일 삭제"""
        pass
