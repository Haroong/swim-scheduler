"""
FacilityClosure Model

시설 휴무일 정보
"""
from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.base import Base


class FacilityClosure(Base):
    """시설 휴무일 모델"""
    __tablename__ = 'facility_closure'

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility.id', ondelete='CASCADE'), nullable=False)
    notice_id = Column(Integer, ForeignKey('notice.id', ondelete='SET NULL'), nullable=True)
    valid_month = Column(String(7), nullable=False)  # YYYY-MM
    closure_type = Column(Enum('regular', 'holiday', 'specific_date'), nullable=False)
    day_of_week = Column(Enum('월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일'), nullable=True)
    week_pattern = Column(String(20), nullable=True)  # "2,4" = 2,4주차, NULL = 매주
    closure_date = Column(Date, nullable=True)  # 특정 날짜 휴무
    reason = Column(String(200), nullable=True)

    # Relationships
    facility = relationship("Facility", back_populates="closures")
    notice = relationship("Notice", back_populates="closures")

    def __repr__(self):
        return f"<FacilityClosure(id={self.id}, facility_id={self.facility_id}, type='{self.closure_type}')>"
