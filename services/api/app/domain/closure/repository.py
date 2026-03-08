"""
Closure Repository Interface

휴무일 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.closure.model import FacilityClosure


class ClosureRepository(ABC):
    """휴무일 Repository 인터페이스"""

    @abstractmethod
    def find_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> List[FacilityClosure]:
        """시설 + 월별 휴무일 조회"""
        pass

    @abstractmethod
    def find_first_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> Optional[FacilityClosure]:
        """시설 + 월별 첫 번째 휴무일 조회"""
        pass
