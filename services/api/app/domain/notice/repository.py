"""
Notice Repository Interface

공지사항 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.notice.model import Notice


class NoticeRepository(ABC):
    """공지사항 Repository 인터페이스"""

    @abstractmethod
    def find_by_facility_and_month(
        self, facility_id: int, valid_date: str
    ) -> Optional[Notice]:
        """시설 + 월별 공지사항 조회"""
        pass

    @abstractmethod
    def find_by_valid_month(self, valid_month: str) -> List[Notice]:
        """해당 월 모든 공지사항 조회"""
        pass
