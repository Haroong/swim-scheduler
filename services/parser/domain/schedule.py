"""
Schedule 도메인 엔티티

DB의 swim_schedule, swim_session 테이블을 표현하는 엔티티
비즈니스 로직 포함
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SwimSession:
    """
    수영 세션 엔티티 (swim_session 테이블)

    비즈니스 로직:
    - 세션 길이 계산
    - 시간 유효성 검증
    """
    id: Optional[int]          # DB PK (생성 전에는 None)
    schedule_id: int           # Schedule FK
    session_name: str          # 세션명 (아침, 점심, 저녁 등)
    start_time: str            # 시작 시간 (HH:MM)
    end_time: str              # 종료 시간 (HH:MM)
    capacity: Optional[int] = None    # 정원
    lanes: Optional[int] = None       # 레인 수

    def duration_minutes(self) -> int:
        """
        세션 길이 계산 (분)

        Returns:
            세션 길이 (분 단위)

        Example:
            >>> session = SwimSession(..., start_time="08:00", end_time="08:50")
            >>> session.duration_minutes()
            50
        """
        try:
            start_h, start_m = map(int, self.start_time.split(":"))
            end_h, end_m = map(int, self.end_time.split(":"))
            return (end_h * 60 + end_m) - (start_h * 60 + start_m)
        except (ValueError, AttributeError):
            return 0

    def is_valid_time_format(self) -> bool:
        """시간 형식 유효성 검증 (HH:MM)"""
        import re
        time_pattern = r"^\d{1,2}:\d{2}$"
        return bool(re.match(time_pattern, self.start_time)) and \
               bool(re.match(time_pattern, self.end_time))

    def __str__(self) -> str:
        return f"SwimSession({self.session_name} {self.start_time}-{self.end_time})"


@dataclass
class DaySchedule:
    """
    요일별 스케줄 엔티티 (swim_schedule 테이블)

    비즈니스 로직:
    - 하루 총 정원 계산
    - 세션 수 계산
    """
    id: Optional[int]          # DB PK (생성 전에는 None)
    facility_id: int           # Facility FK
    day_type: str              # 평일, 토요일, 일요일
    season: Optional[str] = None       # 하절기, 동절기, None (계절 구분 없음)
    valid_month: Optional[str] = None  # 적용 월 (YYYY-MM)
    sessions: List[SwimSession] = None # 세션 목록

    def __post_init__(self):
        if self.sessions is None:
            self.sessions = []

    def total_capacity(self) -> int:
        """
        하루 총 정원 계산

        Returns:
            모든 세션의 정원 합계

        Example:
            >>> schedule = DaySchedule(...)
            >>> schedule.sessions = [
            ...     SwimSession(..., capacity=30),
            ...     SwimSession(..., capacity=40)
            ... ]
            >>> schedule.total_capacity()
            70
        """
        return sum(s.capacity or 0 for s in self.sessions)

    def session_count(self) -> int:
        """세션 개수"""
        return len(self.sessions)

    def add_session(self, session: SwimSession):
        """세션 추가"""
        self.sessions.append(session)

    def get_sessions_by_time_range(self, start_hour: int, end_hour: int) -> List[SwimSession]:
        """
        특정 시간대의 세션 필터링

        Args:
            start_hour: 시작 시간 (시)
            end_hour: 종료 시간 (시)

        Returns:
            해당 시간대에 시작하는 세션 목록
        """
        result = []
        for session in self.sessions:
            try:
                session_start_hour = int(session.start_time.split(":")[0])
                if start_hour <= session_start_hour < end_hour:
                    result.append(session)
            except (ValueError, AttributeError):
                continue
        return result

    def __str__(self) -> str:
        season_str = f" ({self.season})" if self.season else ""
        return f"DaySchedule({self.day_type}{season_str}, {len(self.sessions)} sessions)"
