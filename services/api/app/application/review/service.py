"""
Review Service
리뷰 CRUD 비즈니스 로직
"""
import logging
from typing import List, Optional

import bcrypt

from app.domain.review.model import Review
from app.domain.review.repository import ReviewRepository

logger = logging.getLogger(__name__)


class ReviewService:
    """리뷰 서비스"""

    def __init__(self, review_repo: ReviewRepository):
        self._review_repo = review_repo

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def get_reviews(self, facility_id: int) -> List[Review]:
        """시설별 리뷰 최신순 조회"""
        return self._review_repo.find_by_facility_id(facility_id)

    def get_review_stats(self, facility_id: int) -> dict:
        """평균 별점 + 리뷰 수"""
        return self._review_repo.get_stats(facility_id)

    def create_review(
        self,
        facility_id: int,
        nickname: str,
        password: str,
        rating: int,
        content: str
    ) -> Review:
        """리뷰 생성"""
        review = Review(
            facility_id=facility_id,
            nickname=nickname,
            password_hash=self._hash_password(password),
            rating=rating,
            content=content
        )
        return self._review_repo.save(review)

    def update_review(
        self,
        review_id: int,
        password: str,
        rating: Optional[int] = None,
        content: Optional[str] = None
    ) -> Optional[Review]:
        """비밀번호 검증 후 리뷰 수정. 비밀번호 불일치 시 None 반환."""
        review = self._review_repo.find_by_id(review_id)
        if not review:
            raise ValueError("리뷰를 찾을 수 없습니다.")

        if not self._verify_password(password, review.password_hash):
            return None

        if rating is not None:
            review.rating = rating
        if content is not None:
            review.content = content

        return self._review_repo.save(review)

    def delete_review(self, review_id: int, password: str) -> Optional[bool]:
        """비밀번호 검증 후 리뷰 삭제. 비밀번호 불일치 시 None 반환."""
        review = self._review_repo.find_by_id(review_id)
        if not review:
            raise ValueError("리뷰를 찾을 수 없습니다.")

        if not self._verify_password(password, review.password_hash):
            return None

        self._review_repo.delete(review)
        return True
