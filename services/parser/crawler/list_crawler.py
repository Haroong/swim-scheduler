"""
게시글 목록 크롤러
성남시청소년청년재단 수영장 공지 게시판에서 게시글 목록을 수집
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://www.snyouth.or.kr"
BOARD_URL = f"{BASE_URL}/fmcs/289"


@dataclass
class PostSummary:
    """게시글 요약 정보"""
    post_id: str           # action-value 값
    title: str             # 게시글 제목
    facility_name: str     # 시설명
    date: str              # 등록일자
    has_attachment: bool   # 첨부파일 여부
    detail_url: str        # 상세 페이지 URL


class ListCrawler:
    """게시판 목록 크롤러"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def get_posts(self, keyword: str = "자유수영", max_pages: int = 5, search_field: str = "Ti") -> List[PostSummary]:
        """
        키워드로 게시글 검색하여 목록 반환

        Args:
            keyword: 검색 키워드 (기본값: "자유수영")
            max_pages: 최대 검색할 페이지 수
            search_field: 검색 대상 (Ti: 제목, Co: 내용, ALL: 전체)

        Returns:
            PostSummary 객체 리스트
        """
        all_posts = []

        for page in range(1, max_pages + 1):
            logger.info(f"페이지 {page} 크롤링 중...")
            posts = self._crawl_page(keyword, page, search_field)

            if not posts:
                logger.info(f"페이지 {page}에서 더 이상 게시글 없음. 종료.")
                break

            all_posts.extend(posts)
            time.sleep(0.5)  # 서버 부하 방지

        logger.info(f"총 {len(all_posts)}개 게시글 수집 완료")
        return all_posts

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

            # 시설명 (두 번째 컬럼)
            facility_name = cols[1].get_text(strip=True)

            # 첨부파일 여부 (네 번째 컬럼)
            attach_col = cols[3]
            has_attachment = attach_col.find("img") is not None or attach_col.find("a") is not None

            # 등록일자 (다섯 번째 컬럼)
            date = cols[4].get_text(strip=True)

            # 상세 페이지 URL 생성
            detail_url = f"{BOARD_URL}?action=read&action-value={post_id}"

            # 제외 키워드가 포함된 게시글 필터링
            exclude_keywords = ['추첨', '상담', '방문']
            if any(kw in title for kw in exclude_keywords):
                logger.debug(f"제외 키워드 게시글: {title}")
                continue

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
