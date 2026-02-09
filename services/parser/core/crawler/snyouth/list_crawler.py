"""
게시글 목록 크롤러
성남시청소년청년재단 수영장 공지 게시판에서 게시글 목록을 수집
"""
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging
import requests

from core.crawler.base.list_crawler import BaseListCrawler
from core.models.crawler import PostSummary
from infrastructure.utils.http_utils import create_session

logger = logging.getLogger(__name__)

BASE_URL = "https://www.snyouth.or.kr"
BOARD_URL = f"{BASE_URL}/fmcs/289"


class ListCrawler(BaseListCrawler):
    """
    성남시청소년청년재단 게시판 목록 크롤러

    HTML 파싱 방식으로 게시글 목록 수집
    """

    def _init_session(self):
        """HTTP 세션 초기화"""
        return create_session()

    def _crawl_page(self, keyword: str, page: int, search_field: str = "Ti") -> List[PostSummary]:
        """단일 페이지 크롤링"""
        params = {
            "search_field": search_field,  # Ti: 제목, Co: 내용, ALL: 전체
            "search_word": keyword,
            "page": page
        }

        try:
            response = self.session.get(BOARD_URL, params=params, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"페이지 요청 실패: {e}")
            return []

        return self._parse_list_page(response.text)

    def _parse_list_page(self, html: str) -> List[PostSummary]:
        """목록 페이지 HTML 파싱"""
        soup = BeautifulSoup(html, "html.parser")
        posts = []

        # 테이블의 tbody에서 각 행(tr)을 찾음
        table = soup.find("table")
        if not table:
            logger.warning("게시판 테이블을 찾을 수 없음")
            return []

        tbody = table.find("tbody")
        if not tbody:
            # tbody가 없으면 table에서 직접 tr 찾기
            rows = table.find_all("tr")
        else:
            rows = tbody.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            # 제목 컬럼에서 링크 추출
            title_col = cols[2]
            link = title_col.find("a")

            if not link:
                continue

            href = link.get("href", "")
            title = link.get_text(strip=True)

            # action-value 추출
            post_id = self._extract_post_id(href)
            if not post_id:
                continue

            # 시설명 (두 번째 컬럼에서 <strong class="loc ..."> 태그 찾기)
            facility_col = cols[1]
            facility_tag = facility_col.find("strong", class_=lambda x: x and "loc" in x)
            facility_name = facility_tag.get_text(strip=True) if facility_tag else ""

            # 첨부파일 여부 (네 번째 컬럼)
            attach_col = cols[3]
            has_attachment = attach_col.find("img") is not None or attach_col.find("a") is not None

            # 등록일자 (다섯 번째 컬럼)
            date = cols[4].get_text(strip=True)

            # 상세 페이지 URL 생성
            detail_url = f"{BOARD_URL}?action=read&action-value={post_id}"

            post = PostSummary(
                post_id=post_id,
                title=title,
                facility_name=facility_name,
                date=date,
                has_attachment=has_attachment,
                detail_url=detail_url
            )
            posts.append(post)
            logger.debug(f"게시글 발견: {title}")

        return posts

    def _extract_post_id(self, href: str) -> Optional[str]:
        """href에서 action-value 추출"""
        # ?action=read&action-value=xxx 형식
        if "action-value=" in href:
            parts = href.split("action-value=")
            if len(parts) > 1:
                # 추가 파라미터가 있을 수 있으므로 & 기준으로 분리
                return parts[1].split("&")[0]
        return None


# 테스트용 코드
if __name__ == "__main__":
    crawler = ListCrawler()

    # "수영" 키워드로 검색 (자유수영보다 넓은 범위)
    posts = crawler.get_posts(keyword="수영", max_pages=2)

    for post in posts:
        print(f"[{post.date}] {post.facility_name} - {post.title}")
        print(f"  URL: {post.detail_url}")
        print(f"  첨부: {'있음' if post.has_attachment else '없음'}")
        print()
