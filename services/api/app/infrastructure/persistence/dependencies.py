"""
FastAPI Depends() 팩토리 함수

Repository → Service DI 체인
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.facility_repository import SqlAlchemyFacilityRepository
from app.infrastructure.persistence.schedule_repository import SqlAlchemyScheduleRepository
from app.infrastructure.persistence.closure_repository import SqlAlchemyClosureRepository
from app.infrastructure.persistence.notice_repository import SqlAlchemyNoticeRepository
from app.infrastructure.persistence.fee_repository import SqlAlchemyFeeRepository
from app.infrastructure.persistence.review_repository import SqlAlchemyReviewRepository
from app.infrastructure.persistence.user_repository import SqlAlchemyUserRepository
from app.application.schedule.service import ScheduleService
from app.application.review.service import ReviewService
from app.application.auth.service import AuthService


# Repository factories
def get_facility_repository(db: Session = Depends(get_db)):
    return SqlAlchemyFacilityRepository(db)


def get_schedule_repository(db: Session = Depends(get_db)):
    return SqlAlchemyScheduleRepository(db)


def get_closure_repository(db: Session = Depends(get_db)):
    return SqlAlchemyClosureRepository(db)


def get_notice_repository(db: Session = Depends(get_db)):
    return SqlAlchemyNoticeRepository(db)


def get_fee_repository(db: Session = Depends(get_db)):
    return SqlAlchemyFeeRepository(db)


def get_review_repository(db: Session = Depends(get_db)):
    return SqlAlchemyReviewRepository(db)


def get_user_repository(db: Session = Depends(get_db)):
    return SqlAlchemyUserRepository(db)


# Service factories
def get_schedule_service(
    facility_repo=Depends(get_facility_repository),
    schedule_repo=Depends(get_schedule_repository),
    closure_repo=Depends(get_closure_repository),
    notice_repo=Depends(get_notice_repository),
    fee_repo=Depends(get_fee_repository),
):
    return ScheduleService(facility_repo, schedule_repo, closure_repo, notice_repo, fee_repo)


def get_review_service(
    review_repo=Depends(get_review_repository),
):
    return ReviewService(review_repo)


def get_auth_service(
    user_repo=Depends(get_user_repository),
):
    return AuthService(user_repo)
