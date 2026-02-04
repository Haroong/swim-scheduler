"""
Facility Model

수영장 시설 정보
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.domain.base import Base


class Facility(Base):
    """시설 모델"""
    __tablename__ = 'facility'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    # Relationships
    schedules = relationship("SwimSchedule", back_populates="facility", lazy="selectin")
    fees = relationship("Fee", back_populates="facility", lazy="selectin")
    notices = relationship("Notice", back_populates="facility", lazy="selectin")
    closures = relationship("FacilityClosure", back_populates="facility", lazy="selectin")

    def __repr__(self):
        return f"<Facility(id={self.id}, name='{self.name}')>"
