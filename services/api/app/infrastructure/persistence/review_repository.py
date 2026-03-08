"""SqlAlchemy Review Repository 구현체"""
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.review.model import Review
from app.domain.review.repository import ReviewRepository


class SqlAlchemyReviewRepository(ReviewRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_id(self, review_id: int) -> Optional[Review]:
        return self._db.get(Review, review_id)

    def find_by_facility_id(self, facility_id: int) -> List[Review]:
        stmt = (
            select(Review)
            .where(Review.facility_id == facility_id)
            .order_by(Review.created_at.desc())
        )
        return list(self._db.execute(stmt).scalars().all())

    def get_stats(self, facility_id: int) -> dict:
        stmt = (
            select(
                func.avg(Review.rating).label('average_rating'),
                func.count(Review.id).label('review_count')
            )
            .where(Review.facility_id == facility_id)
        )
        row = self._db.execute(stmt).one()
        return {
            "facility_id": facility_id,
            "average_rating": round(float(row.average_rating), 1) if row.average_rating else 0,
            "review_count": row.review_count
        }

    def save(self, review: Review) -> Review:
        self._db.add(review)
        self._db.commit()
        self._db.refresh(review)
        return review

    def delete(self, review: Review) -> None:
        self._db.delete(review)
        self._db.commit()
