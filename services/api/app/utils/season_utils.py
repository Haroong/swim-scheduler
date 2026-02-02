"""Season Utility Functions - 계절 관련 유틸리티 함수"""
from typing import Optional

# 요일 매핑 (weekday 인덱스 -> 한글 약자)
WEEKDAY_MAP = {
    0: "월",
    1: "화",
    2: "수",
    3: "목",
    4: "금",
    5: "토",
    6: "일"
}


def get_weekday_short(weekday: int) -> str:
    """weekday 인덱스(0=월요일)를 한글 약자로 변환"""
    return WEEKDAY_MAP.get(weekday, "")


def should_include_session(applicable_days: Optional[str], weekday: int) -> bool:
    """
    세션이 특정 요일에 적용되는지 판단

    Args:
        applicable_days: 적용 요일 (None=전체, "수"=수요일만, "월,수,금"=월수금)
        weekday: 요일 인덱스 (0=월요일, 6=일요일)

    Returns:
        해당 요일에 세션이 적용되면 True
    """
    if not applicable_days:  # None 또는 빈 문자열 → 전체 적용
        return True

    target_day = get_weekday_short(weekday)
    # "월,수,금" 형태 또는 "수" 형태 모두 처리
    applicable_list = [d.strip() for d in applicable_days.split(",")]
    return target_day in applicable_list


def get_season_from_month(month: int) -> str:
    """월 번호로부터 계절 반환 (3~10월=하절기, 11~2월=동절기)"""
    if not 1 <= month <= 12:
        raise ValueError(f"Invalid month: {month}")

    return "하절기" if 3 <= month <= 10 else "동절기"


def should_include_schedule(schedule_season: Optional[str], target_season: str) -> bool:
    """
    스케줄이 대상 계절에 포함되어야 하는지 판단
    - Empty/None season: 항상 True (연중 운영)
    - 일치하는 계절: True
    - 다른 계절: False
    """
    if not schedule_season:  # "", None
        return True
    return schedule_season == target_season
