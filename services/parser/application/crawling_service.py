"""
크롤링 실행 서비스
- 기관별 크롤러를 사용하여 데이터 수집
- 기본 스케줄 및 월별 공지사항 크롤링
"""
import logging
from typing import List
from core.crawler.factory import CrawlerFactory
from core.models.crawler import PostSummary, PostDetail
from core.models.facility import Organization

logger = logging.getLogger(__name__)


class CrawlingService:
    """크롤링 실행 서비스"""

    def __init__(self, org: Organization):
        """
        Args:
            org: 기관 (Organization enum)
        """
        self.org = org
        self.list_crawler, self.detail_crawler, self.facility_crawler = CrawlerFactory.create(org)

    def crawl_base_schedules(self) -> List[dict]:
        """
        기본 스케줄 크롤링 (이용안내 페이지)

        Returns:
            시설 기본 정보 리스트
        """
        logger.info(f"[{self.org.value}] 기본 스케줄 크롤링 시작...")
        facilities = self.facility_crawler.crawl_all_facilities()

        # dict 형태로 변환
        result = [self.facility_crawler.to_dict(f) for f in facilities]

        logger.info(f"[{self.org.value}] 기본 스케줄 크롤링 완료: {len(result)}개 시설")
        return result

    def crawl_monthly_notices(self, keyword: str = "수영", max_pages: int = 5) -> List[PostDetail]:
        """
        월별 공지사항 크롤링

        Args:
            keyword: 검색 키워드
            max_pages: 최대 페이지 수

        Returns:
            게시글 상세 정보 리스트
        """
        logger.info(f"[{self.org.value}] 월별 공지사항 크롤링 시작...")

        # snhdc: API가 목록에서 이미 content를 제공하므로 직접 상세 정보 수집
        if self.org == Organization.SNHDC:
            details = self.list_crawler.get_posts_with_details(keyword, max_pages)
            logger.info(f"[{self.org.value}] 상세 정보 수집 완료: {len(details)}개")
            return details

        # snyouth: 목록 → 상세 순서로 크롤링
        # 1. 목록 수집
        posts: List[PostSummary] = self.list_crawler.get_posts(keyword, max_pages)
        logger.info(f"[{self.org.value}] 게시글 목록: {len(posts)}개")

        # 2. 상세 정보 수집 (시설명 전달)
        details = []
        for post in posts:
            detail = self.detail_crawler.get_detail(post.detail_url, facility_name=post.facility_name)
            if detail:
                details.append(detail)

        logger.info(f"[{self.org.value}] 상세 정보 수집 완료: {len(details)}개")
        return details
