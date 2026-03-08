"""
Fee Repository Interface

이용료 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List

from app.domain.fee.model import Fee


class FeeRepository(ABC):
    """이용료 Repository 인터페이스"""

    @abstractmethod
    def find_by_facility_id(self, facility_id: int) -> List[Fee]:
        """시설 ID로 이용료 목록 조회"""
        pass
