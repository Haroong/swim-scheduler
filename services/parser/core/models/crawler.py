"""
크롤러 DTO
크롤링 과정에서 사용되는 데이터 전송 객체
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PostSummary:
    """
    게시글 목록 DTO (크롤러 간 공통)

    모든 기관의 ListCrawler가 반환하는 표준 형식
    """
    post_id: str           # 게시글 고유 ID
    title: str             # 게시글 제목
    facility_name: str     # 시설명
    date: str              # 등록일자
    has_attachment: bool   # 첨부파일 여부
    detail_url: str        # 상세 페이지 URL

    # 선택적 필드 (기관에 따라 있을 수도 있음)
    author: str | None = None
    view_count: int | None = None


@dataclass
class Attachment:
    """첨부파일 정보 DTO"""
    filename: str          # 파일명
    file_size: str         # 파일 크기 (문자열, 예: "1.5MB")
    file_ext: str          # 확장자 (예: "hwp", "pdf")
    download_url: str      # 다운로드 URL


@dataclass
class PostDetail:
    """
    게시글 상세 DTO

    DetailCrawler가 반환하는 표준 형식
    """
    post_id: str                      # 게시글 고유 ID
    title: str                        # 게시글 제목
    facility_name: str                # 시설명
    date: str                         # 등록일자
    content_html: str                 # 본문 HTML
    content_text: str                 # 본문 텍스트 (HTML 태그 제거)
    attachments: list[Attachment]     # 첨부파일 목록
    source_url: str                   # 원본 URL

    # 선택적 필드
    author: str | None = None
    view_count: int | None = None

    @property
    def has_attachment(self) -> bool:
        """첨부파일 존재 여부"""
        return len(self.attachments) > 0

    def get_attachments_by_ext(self, ext: str) -> list[Attachment]:
        """특정 확장자의 첨부파일만 필터링"""
        return [att for att in self.attachments if att.file_ext.lower() == ext.lower()]


@dataclass
class WeekdayScheduleItem:
    """평일 스케줄 항목"""
    start_time: str                         # 시작 시간 (HH:MM)
    end_time: str                           # 종료 시간 (HH:MM)
    days: list[str] = field(default_factory=lambda: ["월", "화", "수", "목", "금"])
    type: str = ""                          # 세션 타입 (아침, 점심, 저녁 등)
    capacity: int = 0                       # 정원
    notes: str = ""                         # 비고


@dataclass
class WeekendSessionItem:
    """주말 세션 항목"""
    start_time: str                         # 시작 시간 (HH:MM)
    end_time: str                           # 종료 시간 (HH:MM)
    capacity: int = 0                       # 정원
    notes: str = ""                         # 비고
    part: str = ""                          # 부 (1부, 2부 등)


@dataclass
class SeasonSchedule:
    """계절별 스케줄"""
    start: str = ""                         # 시작 시간
    end: str = ""                           # 종료 시간
    months: str = ""                        # 적용 월 (예: "3~10월")


@dataclass
class WeekendSchedule:
    """주말 스케줄"""
    saturday: dict = field(default_factory=dict)  # 토요일 스케줄
    sunday: dict = field(default_factory=dict)    # 일요일 스케줄


@dataclass
class FacilityInfoResponse:
    """
    시설 기본 정보 응답 DTO

    FacilityCrawler가 반환하는 표준 형식
    """
    facility_name: str                                      # 시설명
    facility_url: str                                       # 시설 URL
    weekday_schedule: list[WeekdayScheduleItem] = field(default_factory=list)
    weekend_schedule: WeekendSchedule = field(default_factory=WeekendSchedule)
    fees: dict[str, int] = field(default_factory=dict)      # 이용료 (카테고리: 금액)
    notes: list[str] = field(default_factory=list)          # 주의사항
    last_updated: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "facility_name": self.facility_name,
            "facility_url": self.facility_url,
            "weekday_schedule": [
                {
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "days": s.days,
                    "type": s.type,
                    "capacity": s.capacity,
                    "notes": s.notes
                }
                for s in self.weekday_schedule
            ],
            "weekend_schedule": {
                "saturday": self.weekend_schedule.saturday,
                "sunday": self.weekend_schedule.sunday
            },
            "fees": self.fees,
            "notes": self.notes,
            "last_updated": self.last_updated
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FacilityInfoResponse":
        """딕셔너리에서 객체 생성"""
        weekday_schedule = [
            WeekdayScheduleItem(
                start_time=s.get("start_time", ""),
                end_time=s.get("end_time", ""),
                days=s.get("days", ["월", "화", "수", "목", "금"]),
                type=s.get("type", ""),
                capacity=s.get("capacity", 0),
                notes=s.get("notes", "")
            )
            for s in data.get("weekday_schedule", [])
        ]

        weekend_data = data.get("weekend_schedule", {})
        weekend_schedule = WeekendSchedule(
            saturday=weekend_data.get("saturday", {}),
            sunday=weekend_data.get("sunday", {})
        )

        return cls(
            facility_name=data.get("facility_name", ""),
            facility_url=data.get("facility_url", ""),
            weekday_schedule=weekday_schedule,
            weekend_schedule=weekend_schedule,
            fees=data.get("fees", {}),
            notes=data.get("notes", []),
            last_updated=data.get("last_updated", datetime.now().strftime("%Y-%m-%d"))
        )
