"""
크롤러 모듈
- snyouth: 성남시청소년청년재단
- snhdc: 성남도시개발공사
"""
# 성남시청소년청년재단 크롤러
from .snyouth.list_crawler import ListCrawler
from .snyouth.detail_crawler import DetailCrawler
from .snyouth.facility_info_crawler import FacilityInfoCrawler

# Base 클래스
from .base.attachment_downloader import BaseAttachmentDownloader

# 성남도시개발공사 크롤러는 추후 구현
# from .snhdc import ...

__all__ = [
    "ListCrawler",
    "DetailCrawler",
    "FacilityInfoCrawler",
    "BaseAttachmentDownloader",
]
