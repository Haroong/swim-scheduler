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
    def find_by_id(self, notice_id: int) -> Optional[Notice]:
        """ID로 공지사항 조회"""
        pass

    @abstractmethod
    def find_by_facility_id(self, facility_id: int) -> List[Notice]:
        """시설 ID로 공지사항 목록 조회"""
        pass

    @abstractmethod
    def find_by_facility_and_month(
        self, facility_id: int, valid_date: str
    ) -> Optional[Notice]:
        """시설 + 월별 공지사항 조회"""
        pass

    @abstractmethod
    def find_by_source_url(self, source_url: str) -> Optional[Notice]:
        """소스 URL로 공지사항 조회"""
        pass

    @abstractmethod
    def save(self, notice: Notice) -> Notice:
        """공지사항 저장"""
        pass

    @abstractmethod
    def delete(self, notice: Notice) -> None:
        """공지사항 삭제"""
        pass
