"""
Facility Repository Interface

시설 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List


class FacilityRepository(ABC):
    """시설 Repository 인터페이스"""

    @abstractmethod
    def find_all_with_schedule_summary(self) -> List[dict]:
        """시설 목록 + latest_month + schedule_count 집계 조회"""
        pass
