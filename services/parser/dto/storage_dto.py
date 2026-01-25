"""
저장소 DTO
DB 저장 과정에서 사용되는 데이터 전송 객체
"""
from dataclasses import dataclass
from dto.parser_dto import ParsedScheduleData, ScheduleData, FeeData


@dataclass
class SessionStorageData:
    """세션 저장 데이터 (DB 스키마 매핑용)"""
    session_name: str
    start_time: str
    end_time: str
    capacity: int | None
    lanes: int | None


@dataclass
class ScheduleStorageData:
    """스케줄 저장 데이터 (DB 스키마 매핑용)"""
    day_type: str
    season: str | None
    sessions: list[SessionStorageData]


@dataclass
class FeeStorageData:
    """이용료 저장 데이터 (DB 스키마 매핑용)"""
    category: str
    price: int
    note: str


@dataclass
class ScheduleStorageDTO:
    """
    DB 저장용 DTO

    ParsedScheduleData를 DB 스키마에 맞게 변환한 형태
    Repository 레이어에서 사용
    """
    facility_name: str
    schedules: list[ScheduleStorageData]
    fees: list[FeeStorageData]
    valid_month: str           # DB 형식 (YYYY-MM)
    notes: list[str]
    source_url: str

    @classmethod
    def from_parsed_data(cls, parsed: ParsedScheduleData) -> "ScheduleStorageDTO":
        """
        파싱 결과를 저장용 DTO로 변환

        Args:
            parsed: 파싱 결과 DTO

        Returns:
            DB 저장용 DTO
        """
        # 스케줄 변환
        schedules = []
        for schedule in parsed.schedules:
            sessions = [
                SessionStorageData(
                    session_name=sess.session_name,
                    start_time=sess.start_time,
                    end_time=sess.end_time,
                    capacity=sess.capacity,
                    lanes=sess.lanes
                )
                for sess in schedule.sessions
            ]

            schedules.append(ScheduleStorageData(
                day_type=schedule.day_type,
                season=schedule.season if schedule.season else None,
                sessions=sessions
            ))

        # 이용료 변환
        fees = [
            FeeStorageData(
                category=fee.category,
                price=fee.price,
                note=fee.note
            )
            for fee in parsed.fees
        ]

        # valid_month 형식 변환 (예: "2026년 1월" → "2026-01")
        valid_month_db = cls._convert_valid_month(parsed.valid_month)

        return cls(
            facility_name=parsed.facility_name,
            schedules=schedules,
            fees=fees,
            valid_month=valid_month_db,
            notes=parsed.notes,
            source_url=parsed.source_url
        )

    @staticmethod
    def _convert_valid_month(valid_month: str) -> str:
        """
        valid_month 형식 변환
        "2026년 1월" → "2026-01"
        """
        import re

        if not valid_month:
            return ""

        match = re.search(r"(\d{4})년\s*(\d{1,2})월", valid_month)
        if match:
            year = match.group(1)
            month = match.group(2).zfill(2)
            return f"{year}-{month}"

        # 이미 YYYY-MM 형식이면 그대로 반환
        if re.match(r"\d{4}-\d{2}", valid_month):
            return valid_month

        return valid_month[:7] if len(valid_month) >= 7 else valid_month
