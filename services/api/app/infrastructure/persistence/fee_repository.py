"""SqlAlchemy Fee Repository 구현체"""
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.fee.model import Fee
from app.domain.fee.repository import FeeRepository


class SqlAlchemyFeeRepository(FeeRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_facility_id(self, facility_id: int) -> List[Fee]:
        stmt = select(Fee).where(Fee.facility_id == facility_id)
        return list(self._db.execute(stmt).scalars().all())
