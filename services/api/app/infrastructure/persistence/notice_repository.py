"""SqlAlchemy Notice Repository 구현체"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.notice.model import Notice
from app.domain.notice.repository import NoticeRepository


class SqlAlchemyNoticeRepository(NoticeRepository):

    def __init__(self, db: Session):
        self._db = db

    def find_by_facility_and_month(
        self, facility_id: int, valid_date: str
    ) -> Optional[Notice]:
        stmt = (
            select(Notice)
            .where(
                Notice.facility_id == facility_id,
                Notice.valid_date == valid_date
            )
            .limit(1)
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def find_by_valid_month(self, valid_month: str) -> List[Notice]:
        stmt = (
            select(Notice)
            .join(Notice.facility)
            .where(Notice.valid_date == valid_month)
        )
        return list(self._db.execute(stmt).scalars().all())
