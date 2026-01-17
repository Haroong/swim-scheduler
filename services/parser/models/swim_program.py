"""
수영 프로그램 데이터 모델
"""
from dataclasses import dataclass, field
from typing import Optional
import json
from datetime import datetime


@dataclass
class SwimProgram:
    """자유수영 프로그램 정보를 담는 데이터 클래스"""
    pool_name: str                    # 수영장 이름
    program_type: str                 # 프로그램 타입 (자유수영)
    raw_text: str                     # HWP에서 추출한 원문
    source_url: str                   # 원본 게시글 URL
    notice_title: str                 # 게시글 제목
    notice_date: str                  # 게시글 등록일
    attachment_filename: str = ""     # 첨부파일명
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            "pool_name": self.pool_name,
            "program_type": self.program_type,
            "raw_text": self.raw_text,
            "source_url": self.source_url,
            "notice_title": self.notice_title,
            "notice_date": self.notice_date,
            "attachment_filename": self.attachment_filename,
            "created_at": self.created_at
        }

    def to_json(self) -> str:
        """JSON 문자열로 변환"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "SwimProgram":
        """딕셔너리에서 객체 생성"""
        return cls(
            pool_name=data.get("pool_name", ""),
            program_type=data.get("program_type", "자유수영"),
            raw_text=data.get("raw_text", ""),
            source_url=data.get("source_url", ""),
            notice_title=data.get("notice_title", ""),
            notice_date=data.get("notice_date", ""),
            attachment_filename=data.get("attachment_filename", ""),
            created_at=data.get("created_at", datetime.now().isoformat())
        )


# models 패키지 초기화
