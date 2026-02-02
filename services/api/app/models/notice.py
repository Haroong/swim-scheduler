"""
Notice Model

공지사항 정보
"""
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base


class Notice(Base):
    """공지사항 모델"""
    __tablename__ = 'notice'

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility.id'), nullable=False)
    title = Column(String(500), nullable=False)
    source_url = Column(String(500), nullable=False, unique=True)
    valid_date = Column(String(7), nullable=True)  # YYYY-MM
    crawled_at = Column(TIMESTAMP, nullable=True, server_default=func.current_timestamp())

    # Relationships
    facility = relationship("Facility", back_populates="notices")
    closures = relationship("FacilityClosure", back_populates="notice")

    def __repr__(self):
        return f"<Notice(id={self.id}, title='{self.title[:30]}...')>"
