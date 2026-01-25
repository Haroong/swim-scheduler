"""
날짜 검증 유틸리티
valid_month가 notice_date 기준으로 타당한지 검증
"""
import re
import logging

logger = logging.getLogger(__name__)


def validate_valid_month(valid_month: str, notice_date: str) -> bool:
    """
    valid_month가 notice_date 기준으로 타당한지 검증

    Args:
        valid_month: "2025년 11월" 형식
        notice_date: "등록일자2025-10-20" 형식

    Returns:
        유효하면 True, 그렇지 않으면 False
    """
    try:
        # valid_month에서 년월 추출
        vm_match = re.search(r'(\d{4})년\s*(\d{1,2})월', valid_month)
        if not vm_match:
            logger.warning(f"valid_month 형식 오류: {valid_month}")
            return False
        vm_year, vm_month = int(vm_match.group(1)), int(vm_match.group(2))

        # notice_date에서 년월 추출 (YYYY-MM-DD 또는 한글 형식 지원)
        nd_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', notice_date)
        if not nd_match:
            # 한글 형식 시도: "2026년 1월 19일"
            nd_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', notice_date)
        if not nd_match:
            logger.warning(f"notice_date 형식 오류: {notice_date}")
            return False
        nd_year, nd_month = int(nd_match.group(1)), int(nd_match.group(2))

        # 등록일 기준 -2개월 ~ +12개월 범위 허용
        # 예: 2025-10-20 등록 → 2025년 8월 ~ 2026년 10월 허용
        diff_months = (vm_year - nd_year) * 12 + (vm_month - nd_month)

        if -2 <= diff_months <= 12:
            return True
        else:
            logger.warning(
                f"valid_month 범위 초과: {valid_month} "
                f"(등록일: {notice_date}, 차이: {diff_months}개월)"
            )
            return False

    except Exception as e:
        logger.error(f"날짜 검증 실패: {e}")
        return False


def extract_year_month(date_str: str) -> tuple[int, int]:
    """
    날짜 문자열에서 년도와 월 추출

    Args:
        date_str: "등록일자2025-10-20" 또는 "2025-10-20" 형식

    Returns:
        (년도, 월) 튜플
    """
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if not match:
        raise ValueError(f"날짜 형식 오류: {date_str}")

    year = int(match.group(1))
    month = int(match.group(2))

    return year, month
