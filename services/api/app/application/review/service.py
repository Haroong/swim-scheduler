"""
Review Service
리뷰 CRUD 비즈니스 로직
"""
import logging
from typing import List, Optional

import bcrypt
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.review.model import Review

logger = logging.getLogger(__name__)


class ReviewService:
    """리뷰 서비스"""

    @staticmethod
    def _hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def get_reviews(db: Session, facility_id: int) -> List[Review]:
        """시설별 리뷰 최신순 조회"""
        stmt = (
            select(Review)
            .where(Review.facility_id == facility_id)
            .order_by(Review.created_at.desc())
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def get_review_stats(db: Session, facility_id: int) -> dict:
        """평균 별점 + 리뷰 수"""
        stmt = (
            select(
                func.avg(Review.rating).label('average_rating'),
                func.count(Review.id).label('review_count')
            )
            .where(Review.facility_id == facility_id)
        )
        row = db.execute(stmt).one()
        return {
            "facility_id": facility_id,
            "average_rating": round(float(row.average_rating), 1) if row.average_rating else 0,
            "review_count": row.review_count
        }

    @staticmethod
    def create_review(
        db: Session,
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
            password_hash=ReviewService._hash_password(password),
            rating=rating,
            content=content
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def update_review(
        db: Session,
        review_id: int,
        password: str,
        rating: Optional[int] = None,
        content: Optional[str] = None
    ) -> Optional[Review]:
        """비밀번호 검증 후 리뷰 수정. 비밀번호 불일치 시 None 반환."""
        review = db.get(Review, review_id)
        if not review:
            raise ValueError("리뷰를 찾을 수 없습니다.")

        if not ReviewService._verify_password(password, review.password_hash):
            return None

        if rating is not None:
            review.rating = rating
        if content is not None:
            review.content = content

        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete_review(db: Session, review_id: int, password: str) -> Optional[bool]:
        """비밀번호 검증 후 리뷰 삭제. 비밀번호 불일치 시 None 반환."""
        review = db.get(Review, review_id)
        if not review:
            raise ValueError("리뷰를 찾을 수 없습니다.")

        if not ReviewService._verify_password(password, review.password_hash):
            return None

        db.delete(review)
        db.commit()
        return True
