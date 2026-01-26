"""Season Utility Functions - 계절 관련 유틸리티 함수"""
from typing import Optional


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
