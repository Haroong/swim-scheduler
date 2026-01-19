"""
크롤러 DTO
크롤링 과정에서 사용되는 데이터 전송 객체
"""
from dataclasses import dataclass
from typing import List, Optional


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
    author: Optional[str] = None
    view_count: Optional[int] = None


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
    attachments: List[Attachment]     # 첨부파일 목록
    source_url: str                   # 원본 URL

    # 선택적 필드
    author: Optional[str] = None
    view_count: Optional[int] = None

    @property
    def has_attachment(self) -> bool:
        """첨부파일 존재 여부"""
        return len(self.attachments) > 0

    def get_attachments_by_ext(self, ext: str) -> List[Attachment]:
        """특정 확장자의 첨부파일만 필터링"""
        return [att for att in self.attachments if att.file_ext.lower() == ext.lower()]
