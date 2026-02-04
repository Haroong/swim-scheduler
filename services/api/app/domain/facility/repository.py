"""
Facility Repository Interface

시설 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.facility.model import Facility


class FacilityRepository(ABC):
    """시설 Repository 인터페이스"""

    @abstractmethod
    def find_by_id(self, facility_id: int) -> Optional[Facility]:
        """ID로 시설 조회"""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Facility]:
        """이름으로 시설 조회"""
        pass

    @abstractmethod
    def find_all(self) -> List[Facility]:
        """모든 시설 조회"""
        pass

    @abstractmethod
    def save(self, facility: Facility) -> Facility:
        """시설 저장"""
        pass

    @abstractmethod
    def delete(self, facility: Facility) -> None:
        """시설 삭제"""
        pass
