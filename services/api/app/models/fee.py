"""
Fee Model

이용료 정보
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base


class Fee(Base):
    """이용료 모델"""
    __tablename__ = 'fee'

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility.id'), nullable=False)
    category = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)

    # Relationships
    facility = relationship("Facility", back_populates="fees")

    def __repr__(self):
        return f"<Fee(id={self.id}, category='{self.category}', price={self.price})>"
