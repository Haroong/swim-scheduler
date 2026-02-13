"""Closure Utility Functions - 휴무일 관련 유틸리티 함수"""
from datetime import datetime, date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

import holidays

from app.domain.closure.model import FacilityClosure

# 한국 공휴일 캘린더 (한국어 이름 사용)
kr_holidays = holidays.KR(language='ko')

# 요일 매핑 (weekday -> 한글 요일명)
WEEKDAY_TO_KOREAN = {
    0: "월요일",
    1: "화요일",
    2: "수요일",
    3: "목요일",
    4: "금요일",
    5: "토요일",
    6: "일요일"
}


def get_closures(db: Session, facility_id: int, valid_month: str) -> list[FacilityClosure]:
    """
    특정 시설의 휴무일 목록 조회

    Args:
        db: SQLAlchemy Session
        facility_id: 시설 ID
        valid_month: 적용 월 (YYYY-MM)

    Returns:
        휴무일 목록
    """
    stmt = (
        select(FacilityClosure)
        .where(
            FacilityClosure.facility_id == facility_id,
            FacilityClosure.valid_month == valid_month
        )
    )
    return list(db.execute(stmt).scalars().all())


def get_week_of_month(target_date: date) -> int:
    """
    해당 날짜가 그 달의 몇 번째 주인지 계산

    Args:
        target_date: 대상 날짜

    Returns:
        주차 (1~5)
    """
    first_day = target_date.replace(day=1)
    first_weekday = first_day.weekday()

    # 첫째 주의 시작일 계산 (첫 번째 해당 요일)
    day_of_month = target_date.day
    adjusted_day = day_of_month + first_weekday

    return (adjusted_day - 1) // 7 + 1


def matches_regular_pattern(target_date: date, closure: FacilityClosure) -> bool:
    """
    정기휴무 패턴에 매칭되는지 확인

    Args:
        target_date: 확인할 날짜
        closure: 휴무 정보

    Returns:
        매칭 여부
    """
    # 요일 확인
    target_weekday = WEEKDAY_TO_KOREAN.get(target_date.weekday())
    if target_weekday != closure.day_of_week:
        return False

    # 주차 패턴 확인
    if closure.week_pattern is None:
        # 매주 휴무
        return True

    # 특정 주차만 휴무 (예: "2,4" -> 2주차, 4주차)
    week_numbers = [int(w.strip()) for w in closure.week_pattern.split(",")]
    current_week = get_week_of_month(target_date)

    return current_week in week_numbers


def check_facility_closure(
    db: Session,
    facility_id: int,
    target_date: datetime,
    valid_month: str
) -> tuple[bool, Optional[str]]:
    """
    특정 날짜가 휴무일인지 확인

    Args:
        db: SQLAlchemy Session
        facility_id: 시설 ID
        target_date: 확인할 날짜
        valid_month: 적용 월 (YYYY-MM)

    Returns:
        (휴무 여부, 휴무 사유)
    """
    closures = get_closures(db, facility_id, valid_month)
    check_date = target_date.date() if isinstance(target_date, datetime) else target_date

    # 월 전체 휴장 체크 (closure_date가 NULL인 specific_date 레코드)
    for closure in closures:
        if closure.closure_type == "specific_date" and closure.closure_date is None:
            return True, closure.reason or "임시휴장"

    # 공휴일은 기본적으로 휴무 처리
    if check_date in kr_holidays:
        holiday_name = kr_holidays.get(check_date)
        return True, f"공휴일 휴무 ({holiday_name})"

    for closure in closures:
        if closure.closure_type == "specific_date":
            # 특정 날짜 휴무
            if closure.closure_date == check_date:
                return True, closure.reason or "특정일 휴무"

        elif closure.closure_type == "regular":
            # 정기휴무
            if matches_regular_pattern(check_date, closure):
                return True, closure.reason or "정기휴무"

    return False, None
