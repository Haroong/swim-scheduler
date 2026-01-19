"""
게시글 상세 크롤러 추상 베이스 클래스

모든 기관의 DetailCrawler가 상속해야 하는 공통 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Optional
import logging

from dto.crawler_dto import PostDetail

logger = logging.getLogger(__name__)


class BaseDetailCrawler(ABC):
    """
    게시글 상세 크롤러 추상 클래스

    기관별 구현 필요:
    - 게시글 상세 정보 가져오기 (get_detail)
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_detail(self, post_url: str, **kwargs) -> Optional[PostDetail]:
        """
        게시글 상세 정보 가져오기

        Args:
            post_url: 게시글 URL
            **kwargs: 기관별 추가 파라미터 (post_id 등)

        Returns:
            PostDetail 객체 또는 None (실패 시)

        Example:
            >>> def get_detail(self, post_url: str, post_id: str = None):
            ...     response = self.session.get(post_url)
            ...     return self._parse_detail_page(response.text)
        """
        pass

    def validate_detail(self, detail: Optional[PostDetail]) -> bool:
        """
        상세 정보 유효성 검증

        Args:
            detail: PostDetail 객체

        Returns:
            유효성 여부
        """
        if not detail:
            return False

        # 필수 필드 검증
        if not detail.title or not detail.facility_name:
            self.logger.warning("필수 필드 누락: title 또는 facility_name")
            return False

        # 본문 검증 (HTML 또는 텍스트 중 하나는 있어야 함)
        if not detail.content_html and not detail.content_text:
            self.logger.warning("본문 내용 없음")
            return False

        return True

    def extract_text_from_html(self, html: str) -> str:
        """
        HTML에서 텍스트 추출 (공통 유틸리티)

        Args:
            html: HTML 문자열

        Returns:
            텍스트만 추출한 문자열
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        # script, style 태그 제거
        for tag in soup(["script", "style"]):
            tag.decompose()

        # 텍스트 추출
        text = soup.get_text(separator="\n", strip=True)
        return text
