"""
크롤러 모듈
- snyouth: 성남시청소년청년재단
- snhdc: 성남도시개발공사
"""
# 성남시청소년청년재단 크롤러
from .snyouth.list_crawler import ListCrawler
from .snyouth.detail_crawler import DetailCrawler
from .snyouth.facility_info_crawler import FacilityInfoCrawler

# 공통 모듈
from .attachment_downloader import AttachmentDownloader

# 성남도시개발공사 크롤러는 추후 구현
# from .snhdc import ...

__all__ = [
    "ListCrawler",
    "DetailCrawler",
    "FacilityInfoCrawler",
    "AttachmentDownloader"
]
