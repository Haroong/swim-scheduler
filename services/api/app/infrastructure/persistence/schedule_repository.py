"""SqlAlchemy Schedule Repository 구현체"""
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.orm import Session, selectinload

from app.domain.facility.model import Facility
from app.domain.schedule.model import SwimSchedule
from app.domain.schedule.repository import ScheduleRepository


class SqlAlchemyScheduleRepository(ScheduleRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_schedules(
        self,
        facility_name: Optional[str] = None,
        valid_month: Optional[str] = None
    ) -> List[SwimSchedule]:
        stmt = (
            select(SwimSchedule)
            .join(SwimSchedule.facility)
            .options(
                selectinload(SwimSchedule.facility),
                selectinload(SwimSchedule.sessions)
            )
            .order_by(
                SwimSchedule.valid_month.desc(),
                Facility.name,
                SwimSchedule.day_type
            )
        )

        if facility_name:
            stmt = stmt.where(Facility.name == facility_name)
        if valid_month:
            stmt = stmt.where(SwimSchedule.valid_month == valid_month)

        return list(self._db.execute(stmt).scalars().all())

    def find_by_day_type_and_month(
        self, day_type: str, valid_month: str
    ) -> List[SwimSchedule]:
        stmt = (
            select(SwimSchedule)
            .join(SwimSchedule.facility)
            .options(
                selectinload(SwimSchedule.facility),
                selectinload(SwimSchedule.sessions)
            )
            .where(
                SwimSchedule.day_type == day_type,
                SwimSchedule.valid_month == valid_month
            )
            .order_by(Facility.name)
        )
        return list(self._db.execute(stmt).scalars().all())

    def count_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> int:
        stmt = (
            select(func.count(SwimSchedule.id))
            .where(
                SwimSchedule.facility_id == facility_id,
                SwimSchedule.valid_month == valid_month
            )
        )
        return self._db.execute(stmt).scalar()
