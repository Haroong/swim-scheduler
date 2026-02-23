"""
Review Repository Interface

리뷰 데이터 접근을 위한 추상 인터페이스
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.review.model import Review


class ReviewRepository(ABC):
    """리뷰 Repository 인터페이스"""

    @abstractmethod
    def find_by_id(self, review_id: int) -> Optional[Review]:
        """ID로 리뷰 조회"""
        pass

    @abstractmethod
    def find_by_facility_id(self, facility_id: int) -> List[Review]:
        """시설 ID로 리뷰 목록 조회 (최신순)"""
        pass

    @abstractmethod
    def save(self, review: Review) -> Review:
        """리뷰 저장"""
        pass

    @abstractmethod
    def delete(self, review: Review) -> None:
        """리뷰 삭제"""
        pass
