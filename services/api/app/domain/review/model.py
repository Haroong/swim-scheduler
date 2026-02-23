"""
Review Model

수영장 시설 리뷰
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.base import Base


class Review(Base):
    """리뷰 모델"""
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True, autoincrement=True)
    facility_id = Column(Integer, ForeignKey('facility.id', ondelete='CASCADE'), nullable=False)
    nickname = Column(String(50), nullable=False)
    password_hash = Column(String(60), nullable=False)
    rating = Column(Integer, nullable=False)  # 1~5
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, nullable=True, onupdate=func.current_timestamp())

    # Relationships
    facility = relationship("Facility", back_populates="reviews")

    __table_args__ = (
        Index('idx_review_facility_created', 'facility_id', 'created_at'),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, facility_id={self.facility_id}, nickname='{self.nickname}')>"
