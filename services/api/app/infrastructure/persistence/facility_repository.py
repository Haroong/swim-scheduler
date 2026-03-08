"""SqlAlchemy Facility Repository 구현체"""
from typing import List

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.domain.facility.model import Facility
from app.domain.facility.repository import FacilityRepository
from app.domain.schedule.model import SwimSchedule


class SqlAlchemyFacilityRepository(FacilityRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_all_with_schedule_summary(self) -> List[dict]:
        stmt = (
            select(
                Facility.id,
                Facility.name,
                Facility.address,
                Facility.website_url,
                func.max(SwimSchedule.valid_month).label('latest_month'),
                func.count(func.distinct(SwimSchedule.id)).label('schedule_count')
            )
            .outerjoin(SwimSchedule)
            .group_by(Facility.id, Facility.name, Facility.address, Facility.website_url)
            .order_by(Facility.name)
        )

        results = self._db.execute(stmt).all()

        return [
            {
                "facility_id": row.id,
                "facility_name": row.name,
                "address": row.address,
                "website_url": row.website_url,
                "latest_month": row.latest_month if row.latest_month else None,
                "schedule_count": row.schedule_count
            }
            for row in results
        ]
