"""
게시글 목록 크롤러 추상 베이스 클래스

모든 기관의 ListCrawler가 상속해야 하는 공통 인터페이스
템플릿 메서드 패턴 사용
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging
import time

from core.models.crawler import PostSummary

logger = logging.getLogger(__name__)


class BaseListCrawler(ABC):
    """
    게시글 목록 크롤러 추상 클래스

    공통 로직:
    - 페이지네이션 (get_posts)
    - Rate limiting (_sleep)
    - 에러 핸들링

    기관별 구현 필요:
    - HTTP 세션 초기화 (_init_session)
    - 단일 페이지 크롤링 (_crawl_page)
    """

    def __init__(self):
        self.session = self._init_session()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def _init_session(self):
        """
        HTTP 세션 초기화 (기관별 헤더 설정)

        Returns:
            requests.Session 객체

        Example:
            >>> def _init_session(self):
            ...     session = requests.Session()
            ...     session.headers.update({"User-Agent": "..."})
            ...     return session
        """
        pass

    @abstractmethod
    def _crawl_page(self, keyword: str, page: int, **kwargs) -> List[PostSummary]:
        """
        단일 페이지 크롤링 (기관별 API/HTML 파싱 로직)

        Args:
            keyword: 검색 키워드
            page: 페이지 번호
            **kwargs: 기관별 추가 파라미터

        Returns:
            PostSummary 리스트

        Example:
            >>> def _crawl_page(self, keyword: str, page: int, facility_id: str = None):
            ...     response = self.session.post(API_URL, data={...})
            ...     return self._parse_response(response.json())
        """
        pass

    def get_posts(self, keyword: str = "수영", max_pages: int = 5, **kwargs) -> List[PostSummary]:
        """
        공통 크롤링 로직 (템플릿 메서드 패턴)

        페이지네이션, 에러 핸들링, Rate limiting을 공통으로 처리

        Args:
            keyword: 검색 키워드 (기본값: "수영")
            max_pages: 최대 검색할 페이지 수
            **kwargs: 기관별 추가 파라미터 (facility_id 등)

        Returns:
            모든 페이지의 PostSummary 리스트
        """
        all_posts = []

        for page in range(1, max_pages + 1):
            self.logger.info(f"페이지 {page} 크롤링 중...")

            try:
                posts = self._crawl_page(keyword, page, **kwargs)

                if not posts:
                    self.logger.info(f"페이지 {page}에서 더 이상 게시글 없음. 종료.")
                    break

                all_posts.extend(posts)
                self.logger.debug(f"페이지 {page}: {len(posts)}개 게시글 발견")

            except Exception as e:
                self.logger.error(f"페이지 {page} 크롤링 실패: {e}")
                # 실패해도 계속 진행 (다음 페이지 시도)
                continue

            # Rate limiting
            self._sleep()

        self.logger.info(f"총 {len(all_posts)}개 게시글 수집 완료")
        return all_posts

    def _sleep(self, seconds: float = 0.5):
        """
        서버 부하 방지 (Rate limiting)

        Args:
            seconds: 대기 시간 (초)
        """
        time.sleep(seconds)

    def filter_posts_by_keyword(self, posts: List[PostSummary], keyword: str) -> List[PostSummary]:
        """
        게시글 제목에서 키워드 필터링

        Args:
            posts: 게시글 목록
            keyword: 필터링 키워드

        Returns:
            키워드가 포함된 게시글 목록
        """
        return [post for post in posts if keyword in post.title]

    def filter_posts_with_attachment(self, posts: List[PostSummary]) -> List[PostSummary]:
        """
        첨부파일이 있는 게시글만 필터링

        Args:
            posts: 게시글 목록

        Returns:
            첨부파일이 있는 게시글 목록
        """
        return [post for post in posts if post.has_attachment]
