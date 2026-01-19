"""
Notice 도메인 엔티티

DB의 notice 테이블을 표현하는 엔티티
"""
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Notice:
    """
    공지사항 엔티티

    크롤링된 공지사항을 DB에 저장하는 엔티티
    """
    id: int                    # DB PK
    facility_id: int           # 시설 FK
    source_url: str            # 원본 URL (중복 체크용)
    valid_date: Optional[str] = None  # 적용 월 (YYYY-MM 형식)
    notes: Optional[List[str]] = None  # 기타 안내사항 (JSON)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __str__(self) -> str:
        return f"Notice(id={self.id}, facility_id={self.facility_id}, valid_date={self.valid_date})"

    def __repr__(self) -> str:
        return self.__str__()
