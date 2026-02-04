"""
Fee Repository Interface

이용료 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.fee.model import Fee


class FeeRepository(ABC):
    """이용료 Repository 인터페이스"""

    @abstractmethod
    def find_by_id(self, fee_id: int) -> Optional[Fee]:
        """ID로 이용료 조회"""
        pass

    @abstractmethod
    def find_by_facility_id(self, facility_id: int) -> List[Fee]:
        """시설 ID로 이용료 목록 조회"""
        pass

    @abstractmethod
    def save(self, fee: Fee) -> Fee:
        """이용료 저장"""
        pass

    @abstractmethod
    def delete(self, fee: Fee) -> None:
        """이용료 삭제"""
        pass
