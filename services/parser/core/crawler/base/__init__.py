"""
Crawler Base 패키지
모든 기관 크롤러의 추상 베이스 클래스
"""
from core.crawler.base.list_crawler import BaseListCrawler
from core.crawler.base.detail_crawler import BaseDetailCrawler
from core.crawler.base.facility_crawler import BaseFacilityCrawler
from core.crawler.base.attachment_downloader import BaseAttachmentDownloader

__all__ = [
    "BaseListCrawler",
    "BaseDetailCrawler",
    "BaseFacilityCrawler",
    "BaseAttachmentDownloader",
]
