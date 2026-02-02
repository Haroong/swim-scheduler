"""
Schedule Models

수영 스케줄 및 세션 정보
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, Time
from sqlalchemy.orm import relationship

from .base import Base


class SwimSchedule(Base):
    """스케줄 모델"""
    __tablename__ = 'swim_schedule'

    id = Column(Integer, primary_key=True)
    facility_id = Column(Integer, ForeignKey('facility.id'), nullable=False)
    notice_id = Column(Integer, ForeignKey('notice.id', ondelete='CASCADE'), nullable=True)
    day_type = Column(SQLEnum('평일', '토요일', '일요일', name='day_type_enum'), nullable=False)
    season = Column(SQLEnum('하절기', '동절기', name='season_enum'), nullable=True)
    valid_month = Column(String(7), nullable=False)  # YYYY-MM

    # Relationships
    facility = relationship("Facility", back_populates="schedules")
    notice = relationship("Notice", backref="schedules")
    sessions = relationship("SwimSession", back_populates="schedule", lazy="selectin")

    def __repr__(self):
        return f"<SwimSchedule(id={self.id}, facility_id={self.facility_id}, valid_month='{self.valid_month}')>"


class SwimSession(Base):
    """세션 모델"""
    __tablename__ = 'swim_session'

    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey('swim_schedule.id'), nullable=False)
    session_name = Column(String(50), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    capacity = Column(Integer, nullable=True)
    lanes = Column(Integer, nullable=True)
    applicable_days = Column(String(20), nullable=True)  # 적용 요일 (NULL=전체, "수"=수요일만)

    # Relationships
    schedule = relationship("SwimSchedule", back_populates="sessions")

    def __repr__(self):
        return f"<SwimSession(id={self.id}, name='{self.session_name}', time='{self.start_time}-{self.end_time}')>"
