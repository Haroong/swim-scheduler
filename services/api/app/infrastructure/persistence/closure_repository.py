"""SqlAlchemy Closure Repository 구현체"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.closure.model import FacilityClosure
from app.domain.closure.repository import ClosureRepository


class SqlAlchemyClosureRepository(ClosureRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> List[FacilityClosure]:
        stmt = (
            select(FacilityClosure)
            .where(
                FacilityClosure.facility_id == facility_id,
                FacilityClosure.valid_month == valid_month
            )
        )
        return list(self._db.execute(stmt).scalars().all())

    def find_first_by_facility_and_month(
        self, facility_id: int, valid_month: str
    ) -> Optional[FacilityClosure]:
        stmt = (
            select(FacilityClosure)
            .where(
                FacilityClosure.facility_id == facility_id,
                FacilityClosure.valid_month == valid_month
            )
            .limit(1)
        )
        return self._db.execute(stmt).scalar_one_or_none()
