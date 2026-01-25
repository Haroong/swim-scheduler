"""
Crawler Factory

기관별 Crawler 인스턴스를 생성하는 팩토리 클래스
신규 기관 추가 시 여기에 등록만 하면 됨
"""
from typing import Tuple, Dict, Type, List
import logging

from core.crawler.base.list_crawler import BaseListCrawler
from core.crawler.base.detail_crawler import BaseDetailCrawler
from core.crawler.base.facility_crawler import BaseFacilityCrawler

logger = logging.getLogger(__name__)


class CrawlerFactory:
    """
    기관별 Crawler 생성 팩토리

    사용법:
        1. 기관별 Crawler 구현체 작성
        2. CrawlerFactory.register()로 등록
        3. CrawlerFactory.create()로 인스턴스 생성

    Example:
        >>> # 등록
        >>> CrawlerFactory.register(
        ...     "snhdc",
        ...     SnhdcListCrawler,
        ...     SnhdcDetailCrawler,
        ...     SnhdcFacilityCrawler
        ... )
        >>>
        >>> # 사용
        >>> list_crawler, detail_crawler, facility_crawler = CrawlerFactory.create("snhdc")
        >>> posts = list_crawler.get_posts(keyword="수영", max_pages=5)
    """

    # 등록된 크롤러 저장소
    # {org_key: {"list": ListCrawlerClass, "detail": DetailCrawlerClass, "facility": FacilityCrawlerClass}}
    _crawlers: Dict[str, Dict[str, Type]] = {}

    @classmethod
    def register(
        cls,
        org_key: str,
        list_crawler_cls: Type[BaseListCrawler],
        detail_crawler_cls: Type[BaseDetailCrawler],
        facility_crawler_cls: Type[BaseFacilityCrawler]
    ):
        """
        크롤러 등록

        Args:
            org_key: 기관 키 (예: "snhdc", "snyouth")
            list_crawler_cls: ListCrawler 클래스
            detail_crawler_cls: DetailCrawler 클래스
            facility_crawler_cls: FacilityCrawler 클래스

        Example:
            >>> from crawler.snhdc.list_crawler import SnhdcListCrawler
            >>> from crawler.snhdc.detail_crawler import SnhdcDetailCrawler
            >>> from crawler.snhdc.facility_crawler import SnhdcFacilityCrawler
            >>>
            >>> CrawlerFactory.register(
            ...     "snhdc",
            ...     SnhdcListCrawler,
            ...     SnhdcDetailCrawler,
            ...     SnhdcFacilityCrawler
            ... )
        """
        # 타입 검증
        if not issubclass(list_crawler_cls, BaseListCrawler):
            raise TypeError(f"{list_crawler_cls}는 BaseListCrawler를 상속해야 합니다")

        if not issubclass(detail_crawler_cls, BaseDetailCrawler):
            raise TypeError(f"{detail_crawler_cls}는 BaseDetailCrawler를 상속해야 합니다")

        if not issubclass(facility_crawler_cls, BaseFacilityCrawler):
            raise TypeError(f"{facility_crawler_cls}는 BaseFacilityCrawler를 상속해야 합니다")

        cls._crawlers[org_key] = {
            "list": list_crawler_cls,
            "detail": detail_crawler_cls,
            "facility": facility_crawler_cls
        }

        logger.info(f"Crawler 등록 완료: {org_key}")

    @classmethod
    def create(cls, org_key: str) -> Tuple[BaseListCrawler, BaseDetailCrawler, BaseFacilityCrawler]:
        """
        크롤러 인스턴스 생성

        Args:
            org_key: 기관 키 (예: "snhdc", "snyouth")

        Returns:
            (ListCrawler, DetailCrawler, FacilityCrawler) 튜플

        Raises:
            ValueError: 등록되지 않은 기관인 경우

        Example:
            >>> list_crawler, detail_crawler, facility_crawler = CrawlerFactory.create("snhdc")
        """
        if org_key not in cls._crawlers:
            raise ValueError(
                f"등록되지 않은 기관: {org_key}. "
                f"지원하는 기관: {', '.join(cls.get_supported_orgs())}"
            )

        crawlers = cls._crawlers[org_key]

        return (
            crawlers["list"](),
            crawlers["detail"](),
            crawlers["facility"]()
        )

    @classmethod
    def create_list_crawler(cls, org_key: str) -> BaseListCrawler:
        """ListCrawler만 생성"""
        if org_key not in cls._crawlers:
            raise ValueError(f"등록되지 않은 기관: {org_key}")
        return cls._crawlers[org_key]["list"]()

    @classmethod
    def create_detail_crawler(cls, org_key: str) -> BaseDetailCrawler:
        """DetailCrawler만 생성"""
        if org_key not in cls._crawlers:
            raise ValueError(f"등록되지 않은 기관: {org_key}")
        return cls._crawlers[org_key]["detail"]()

    @classmethod
    def create_facility_crawler(cls, org_key: str) -> BaseFacilityCrawler:
        """FacilityCrawler만 생성"""
        if org_key not in cls._crawlers:
            raise ValueError(f"등록되지 않은 기관: {org_key}")
        return cls._crawlers[org_key]["facility"]()

    @classmethod
    def get_supported_orgs(cls) -> List[str]:
        """
        지원하는 기관 목록

        Returns:
            등록된 기관 키 리스트
        """
        return list(cls._crawlers.keys())

    @classmethod
    def is_registered(cls, org_key: str) -> bool:
        """
        기관 등록 여부 확인

        Args:
            org_key: 기관 키

        Returns:
            등록 여부
        """
        return org_key in cls._crawlers

    @classmethod
    def clear(cls):
        """등록된 크롤러 모두 제거 (테스트용)"""
        cls._crawlers.clear()


# ===================================================================
# 기관별 크롤러 등록
# ===================================================================

from core.crawler.snhdc.list_crawler import ListCrawler as SnhdcListCrawler
from core.crawler.snhdc.detail_crawler import DetailCrawler as SnhdcDetailCrawler
from core.crawler.snhdc.facility_info_crawler import FacilityInfoCrawler as SnhdcFacilityCrawler

from core.crawler.snyouth.list_crawler import ListCrawler as SnyouthListCrawler
from core.crawler.snyouth.detail_crawler import DetailCrawler as SnyouthDetailCrawler
from core.crawler.snyouth.facility_info_crawler import FacilityInfoCrawler as SnyouthFacilityCrawler

# SNHDC 등록
CrawlerFactory.register("snhdc", SnhdcListCrawler, SnhdcDetailCrawler, SnhdcFacilityCrawler)

# SNYOUTH 등록
CrawlerFactory.register("snyouth", SnyouthListCrawler, SnyouthDetailCrawler, SnyouthFacilityCrawler)


# ===================================================================
# 사용 예시
# ===================================================================

if __name__ == "__main__":
    # 등록된 기관 확인
    print("지원하는 기관:", CrawlerFactory.get_supported_orgs())
    print()

    # 사용 예시 1: 전체 크롤러 생성
    print("=== SNHDC 크롤러 생성 ===")
    list_crawler, detail_crawler, facility_crawler = CrawlerFactory.create("snhdc")
    print(f"ListCrawler: {list_crawler.__class__.__name__}")
    print(f"DetailCrawler: {detail_crawler.__class__.__name__}")
    print(f"FacilityCrawler: {facility_crawler.__class__.__name__}")
    print()

    # 사용 예시 2: 개별 크롤러 생성
    print("=== SNYOUTH ListCrawler만 생성 ===")
    snyouth_list = CrawlerFactory.create_list_crawler("snyouth")
    print(f"ListCrawler: {snyouth_list.__class__.__name__}")
    print()

    # 사용 예시 3: 실제 크롤링 (주석 처리 - 실제 실행 시 주석 해제)
    # print("=== SNHDC 게시글 목록 크롤링 테스트 ===")
    # posts = list_crawler.get_posts(keyword="수영", max_pages=1)
    # print(f"수집된 게시글: {len(posts)}개")
    # if posts:
    #     print(f"첫 번째 게시글: {posts[0].title}")
