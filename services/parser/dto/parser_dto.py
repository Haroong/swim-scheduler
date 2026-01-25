"""
파서 DTO
파싱 과정에서 사용되는 데이터 전송 객체
"""
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime


@dataclass
class ParseRequest:
    """
    파싱 요청 DTO

    파싱 파이프라인에 전달되는 입력 데이터
    """
    # 입력 소스 (둘 중 하나는 필수)
    file_path: Path | None = None      # 파일 경로 (HWP/PDF)
    raw_text: str | None = None        # 직접 제공된 텍스트

    # 메타데이터 (파싱 힌트로 사용)
    facility_name: str = ""               # 시설명
    notice_date: str = ""                 # 공지 등록일
    source_url: str = ""                  # 원본 URL

    def __post_init__(self):
        """입력 검증"""
        if not self.file_path and not self.raw_text:
            raise ValueError("file_path 또는 raw_text 중 하나는 필수입니다")


@dataclass
class SessionData:
    """세션 데이터 (파싱 결과)"""
    session_name: str          # 세션명 (아침, 점심, 저녁 등)
    start_time: str            # 시작 시간 (HH:MM)
    end_time: str              # 종료 시간 (HH:MM)
    capacity: int | None = None    # 정원
    lanes: int | None = None       # 레인 수


@dataclass
class ScheduleData:
    """스케줄 데이터 (요일별)"""
    day_type: str              # 평일, 토요일, 일요일
    season: str = ""           # 하절기, 동절기, 또는 빈 문자열
    season_months: str = ""    # 적용 월 (예: "3~10월")
    sessions: list[SessionData] = field(default_factory=list)


@dataclass
class FeeData:
    """이용료 데이터"""
    category: str              # 대상 (성인, 청소년, 어린이 등)
    price: int                 # 금액 (원)
    note: str = ""             # 비고


@dataclass
class ParsedScheduleData:
    """
    파싱 결과 DTO

    파싱 파이프라인의 최종 출력 데이터
    """
    facility_name: str                              # 시설명
    schedules: list[ScheduleData] = field(default_factory=list)  # 요일별 스케줄
    fees: list[FeeData] = field(default_factory=list)           # 이용료
    valid_month: str = ""                           # 적용 월 (예: 2026년 1월)
    notes: list[str] = field(default_factory=list)  # 기타 안내사항
    source_url: str = ""                            # 원본 URL
    parsed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (JSON 직렬화용)"""
        return {
            "facility_name": self.facility_name,
            "schedules": [
                {
                    "day_type": s.day_type,
                    "season": s.season,
                    "season_months": s.season_months,
                    "sessions": [
                        {
                            "session_name": sess.session_name,
                            "start_time": sess.start_time,
                            "end_time": sess.end_time,
                            "capacity": sess.capacity,
                            "lanes": sess.lanes
                        }
                        for sess in s.sessions
                    ]
                }
                for s in self.schedules
            ],
            "fees": [
                {"category": f.category, "price": f.price, "note": f.note}
                for f in self.fees
            ],
            "valid_month": self.valid_month,
            "notes": self.notes,
            "source_url": self.source_url,
            "parsed_at": self.parsed_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ParsedScheduleData":
        """딕셔너리에서 객체 생성"""
        schedules = []
        for s in data.get("schedules", []):
            sessions = [
                SessionData(
                    session_name=sess["session_name"],
                    start_time=sess["start_time"],
                    end_time=sess["end_time"],
                    capacity=sess.get("capacity"),
                    lanes=sess.get("lanes")
                )
                for sess in s.get("sessions", [])
            ]
            schedules.append(ScheduleData(
                day_type=s["day_type"],
                season=s.get("season", ""),
                season_months=s.get("season_months", ""),
                sessions=sessions
            ))

        fees = [
            FeeData(
                category=f["category"],
                price=f["price"],
                note=f.get("note", "")
            )
            for f in data.get("fees", [])
        ]

        return cls(
            facility_name=data.get("facility_name", ""),
            schedules=schedules,
            fees=fees,
            valid_month=data.get("valid_month", ""),
            notes=data.get("notes", []),
            source_url=data.get("source_url", ""),
            parsed_at=data.get("parsed_at", datetime.now().isoformat())
        )
