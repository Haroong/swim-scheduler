"""
파싱된 자유수영 데이터 모델
LLM이 추출한 구조화된 데이터를 담는 클래스들
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class SwimSession:
    """자유수영 세션 정보"""
    session_name: str          # 세션명 (아침, 점심, 저녁, 1부, 2부 등)
    start_time: str            # 시작 시간 (HH:MM)
    end_time: str              # 종료 시간 (HH:MM)
    capacity: Optional[int] = None    # 정원
    lanes: Optional[int] = None       # 레인 수


@dataclass
class DaySchedule:
    """요일별 스케줄"""
    day_type: str              # 평일, 토요일, 일요일
    season: str = ""           # 하절기, 동절기, 또는 빈 문자열(계절 구분 없음)
    season_months: str = ""    # 적용 월 (예: "3~10월", "11~2월")
    sessions: List[SwimSession] = field(default_factory=list)


@dataclass
class FeeInfo:
    """이용료 정보"""
    category: str              # 대상 (성인, 청소년, 어린이 등)
    price: int                 # 금액 (원)
    note: str = ""             # 비고


@dataclass
class ParsedSwimData:
    """파싱된 자유수영 정보"""
    facility_name: str                              # 시설명
    schedules: List[DaySchedule] = field(default_factory=list)  # 요일별 스케줄
    fees: List[FeeInfo] = field(default_factory=list)           # 이용료
    valid_month: str = ""                           # 적용 월 (예: 2026년 1월)
    notes: List[str] = field(default_factory=list)  # 기타 안내사항
    source_url: str = ""                            # 원본 URL
    parsed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
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

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "ParsedSwimData":
        """딕셔너리에서 객체 생성"""
        schedules = []
        for s in data.get("schedules", []):
            sessions = [
                SwimSession(
                    session_name=sess["session_name"],
                    start_time=sess["start_time"],
                    end_time=sess["end_time"],
                    capacity=sess.get("capacity"),
                    lanes=sess.get("lanes")
                )
                for sess in s.get("sessions", [])
            ]
            schedules.append(DaySchedule(
                day_type=s["day_type"],
                season=s.get("season", ""),
                season_months=s.get("season_months", ""),
                sessions=sessions
            ))

        fees = [
            FeeInfo(
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
