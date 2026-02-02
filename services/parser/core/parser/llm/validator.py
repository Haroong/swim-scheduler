"""
파싱 결과 검증 모듈
LLM 파싱 결과의 평일/주말 구분이 올바른지 검증
"""
import logging
from typing import Optional, List
from datetime import datetime

from core.models.parser import ParsedScheduleData
from infrastructure.config.logging_config import get_logger

logger = get_logger(__name__)


class ScheduleValidator:
    """스케줄 파싱 결과 검증기"""

    # 일반적인 검증 규칙 (시설별로 다를 수 있음)
    GENERAL_RULES = {
        "early_morning_only_weekday": True,  # 새벽(6시 이전) 운영은 주로 평일만
        "late_evening_mainly_weekday": True,  # 늦은 저녁(19시 이후)도 주로 평일
        "weekend_fewer_sessions": True,  # 주말은 평일보다 세션이 적은 경향
    }

    def __init__(self):
        """검증기 초기화"""
        self.warnings = []
        self.errors = []

    def validate(self, parsed_data: ParsedScheduleData) -> tuple[bool, List[str], List[str]]:
        """
        파싱 결과 검증

        Args:
            parsed_data: 파싱된 스케줄 데이터

        Returns:
            (검증 성공 여부, 경고 메시지 리스트, 오류 메시지 리스트)
        """
        self.warnings = []
        self.errors = []

        facility_name = parsed_data.facility_name

        # 일반 규칙으로 검증
        self._validate_with_general_rules(parsed_data)

        # 추가 일반 검증
        self._validate_general(parsed_data)

        # 로그 출력
        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"[{facility_name}] {warning}")

        if self.errors:
            for error in self.errors:
                logger.error(f"[{facility_name}] {error}")

        return len(self.errors) == 0, self.warnings, self.errors

    def _validate_with_general_rules(self, parsed_data: ParsedScheduleData):
        """일반 규칙으로 검증"""

        # 요일별 스케줄 분리
        weekday_sessions = []
        weekend_sessions = []

        for schedule in parsed_data.schedules:
            day_type = schedule.day_type
            sessions = schedule.sessions

            if day_type == "평일":
                weekday_sessions.extend(sessions)
            elif day_type in ["토요일", "일요일"]:
                weekend_sessions.extend(sessions)

        # 주말이 평일보다 세션이 적은지 확인
        if self.GENERAL_RULES.get("weekend_fewer_sessions"):
            if weekday_sessions and weekend_sessions:
                # 토요일과 일요일 각각의 평균을 계산
                weekend_avg = len(weekend_sessions) / 2  # 토/일 2일로 나눔
                if weekend_avg > len(weekday_sessions):
                    self.warnings.append(
                        f"주말 평균 세션({weekend_avg:.1f})이 평일({len(weekday_sessions)})보다 많음"
                    )

        # 새벽 운영 검증 (6시 이전은 주로 평일만)
        if self.GENERAL_RULES.get("early_morning_only_weekday"):
            for schedule in parsed_data.schedules:
                if schedule.day_type in ["토요일", "일요일"]:
                    for session in schedule.sessions:
                        if session.start_time and session.start_time < "06:00":
                            self.warnings.append(
                                f"주말에 새벽 시간대 발견: {schedule.day_type} {session.start_time}"
                            )

        # 늦은 저녁 검증 (19시 이후는 주로 평일)
        if self.GENERAL_RULES.get("late_evening_mainly_weekday"):
            weekend_late_count = 0
            for schedule in parsed_data.schedules:
                if schedule.day_type in ["토요일", "일요일"]:
                    for session in schedule.sessions:
                        if session.start_time and session.start_time >= "19:00":
                            weekend_late_count += 1

            if weekend_late_count > 0:
                self.warnings.append(
                    f"주말에 늦은 저녁 시간대 {weekend_late_count}개 발견"
                )

    def _validate_general(self, parsed_data: ParsedScheduleData):
        """일반적인 검증"""

        # 1. 평일과 주말 세션이 겹치는지 확인
        weekday_times = set()
        weekend_times = set()

        for schedule in parsed_data.schedules:
            day_type = schedule.day_type
            sessions = schedule.sessions

            for session in sessions:
                time_key = f"{session.start_time}~{session.end_time}"

                if day_type == "평일":
                    weekday_times.add(time_key)
                elif day_type in ["토요일", "일요일"]:
                    weekend_times.add(time_key)

        # 겹치는 시간대 확인
        overlapping = weekday_times & weekend_times
        if overlapping:
            self.warnings.append(
                f"평일과 주말에 동일한 시간대 존재: {list(overlapping)}"
            )

        # 2. 용량 검증 (일반적으로 주말 > 평일)
        weekday_capacity = []
        weekend_capacity = []

        for schedule in parsed_data.schedules:
            day_type = schedule.day_type
            sessions = schedule.sessions

            for session in sessions:
                capacity = session.capacity
                if capacity:
                    if day_type == "평일":
                        weekday_capacity.append(capacity)
                    elif day_type in ["토요일", "일요일"]:
                        weekend_capacity.append(capacity)

        if weekday_capacity and weekend_capacity:
            avg_weekday = sum(weekday_capacity) / len(weekday_capacity)
            avg_weekend = sum(weekend_capacity) / len(weekend_capacity)

            if avg_weekday > avg_weekend * 1.2:  # 평일이 주말보다 20% 이상 많으면 경고
                self.warnings.append(
                    f"평일 평균 정원({avg_weekday:.0f})이 주말({avg_weekend:.0f})보다 많음"
                )

        # 3. valid_month 검증
        if not parsed_data.valid_month:
            self.errors.append("valid_month가 없습니다")
        elif not self._is_valid_month_format(parsed_data.valid_month):
            self.errors.append(f"잘못된 valid_month 형식: {parsed_data.valid_month}")

    def _is_valid_month_format(self, valid_month: str) -> bool:
        """valid_month 형식 검증 (YYYY년 M월)"""
        import re
        pattern = r"^\d{4}년 \d{1,2}월$"
        return bool(re.match(pattern, valid_month))


def validate_and_fix(parsed_data: ParsedScheduleData) -> ParsedScheduleData:
    """
    파싱 결과를 검증하고 가능한 경우 자동 수정

    Args:
        parsed_data: 파싱된 데이터

    Returns:
        검증/수정된 데이터
    """
    validator = ScheduleValidator()
    is_valid, warnings, errors = validator.validate(parsed_data)

    if not is_valid:
        logger.warning(f"[{parsed_data.facility_name}] 데이터 자동 수정 시도")

        # 평일/주말 시간대가 뒤바뀐 경우 교정 (일반적인 패턴 기반)
        for schedule in parsed_data.schedules:
            sessions = schedule.sessions

            if schedule.day_type == "평일":
                # 평일인데 세션이 너무 적고, 새벽/저녁 시간이 없으면 주말일 가능성
                has_early_morning = any(s.start_time < "06:00" for s in sessions if s.start_time)
                has_late_evening = any(s.start_time >= "19:00" for s in sessions if s.start_time)

                if len(sessions) <= 3 and not has_early_morning and not has_late_evening:
                    logger.info(f"평일 -> 주말로 자동 수정 (세션 {len(sessions)}개, 새벽/저녁 없음)")
                    schedule.day_type = "일요일"

            elif schedule.day_type in ["토요일", "일요일"]:
                # 주말인데 새벽이나 늦은 저녁이 있으면 평일일 가능성
                has_early_morning = any(s.start_time < "06:00" for s in sessions if s.start_time)
                has_late_evening = any(s.start_time >= "19:00" for s in sessions if s.start_time)

                if has_early_morning or has_late_evening:
                    logger.info(f"주말 -> 평일로 자동 수정 (새벽/저녁 시간 존재)")
                    schedule.day_type = "평일"

    return parsed_data